import math
from unittest.mock import patch

from django.core.cache import cache
from django.test import TestCase

from . import learning


class GuidedLearningTests(TestCase):
    def setUp(self):
        cache.clear()

    def call(self, mode, **data):
        return self.client.post(f'/api/nonlinear/learning/{mode}/', data, content_type='application/json')

    def start(self, topic):
        with patch('nonlinear.learning.secrets.randbelow', return_value=0):
            response = self.call('practice', action='start', topic=topic)
        self.assertEqual(response.status_code, 200)
        return response.json()

    def answer(self, state, **data):
        response = self.call('practice', action='check', id=state['id'], step=state['step'], **data)
        self.assertEqual(response.status_code, 200, response.content)
        return response.json()

    def advance(self, state, **data):
        answer = self.answer(state, **data)
        self.assertTrue(answer['correct'], answer)
        return answer['state']

    def test_theory_precedes_calculation_and_wrong_method_keeps_stage(self):
        state = self.start('biseccion')
        rejected = self.answer(state, choice='linear')
        self.assertFalse(rejected['correct'])
        self.assertEqual(rejected['state']['step'], 0)
        self.assertIn('función', rejected['feedback'])
        state = self.advance(state, choice='root')
        rejected = self.answer(state, choice='newton')
        self.assertFalse(rejected['correct'])
        self.assertEqual(rejected['state']['step'], 1)
        self.assertNotIn('fields', rejected['state'])

    def test_cannot_skip_or_replay_stages(self):
        state = self.start('newton')
        self.assertEqual(self.call('practice', action='check', id=state['id'], step=3, x=1.4).status_code, 400)
        self.advance(state, choice='root')
        self.assertEqual(self.call('practice', action='check', id=state['id'], step=0, choice='root').status_code, 400)

    def test_bisection_accepts_alternative_valid_interval_and_rounded_values(self):
        state = self.start('biseccion')
        state = self.advance(state, choice='root')
        state = self.advance(state, choice='bisection')
        invalid = self.answer(state, a=2, b=3)
        self.assertFalse(invalid['correct'])
        state = self.advance(state, a=.5, b=2)
        state = self.advance(state, x=1.25)
        state = self.advance(state, bound=.75, residual=.4375)
        self.assertTrue(state['done'])
        self.assertIn('a=0.5', state['next_url'])

    def test_newton_rejects_zero_derivative_and_accepts_scientific_notation(self):
        state = self.start('newton')
        state = self.advance(state, choice='root')
        state = self.advance(state, choice='newton')
        self.assertFalse(self.answer(state, x0=0)['correct'])
        state = self.advance(state, x0=1.5)
        state = self.advance(state, x='1.416667')
        state = self.advance(state, bound='8.3333333e-2', residual='0.00694444')
        self.assertTrue(state['done'])

    def test_errors_require_interpretation_of_tolerance(self):
        state = self.start('errores')
        state = self.advance(state, choice='error')
        state = self.advance(state, choice='absolute')
        state = self.advance(state, v=10, approx=9.8)
        self.assertFalse(self.answer(state, x=-.2)['correct'])
        state = self.advance(state, x=.2)
        self.assertFalse(self.answer(state, relative=.02, percentage=2, decision='yes')['correct'])
        state = self.advance(state, relative=.02, percentage=2, decision='no')
        self.assertTrue(state['done'])

    def test_session_resumes_without_leaking_answers(self):
        state = self.start('newton')
        state = self.advance(state, choice='root')
        response = self.call('practice', action='resume').json()
        self.assertEqual(response, state)
        self.assertNotIn('correct', response)
        self.assertNotIn('values', response)

    def test_invalid_numbers_and_topics_are_json_errors(self):
        self.assertEqual(self.call('practice', action='start', topic=[]).status_code, 400)
        state = self.start('newton')
        state = self.advance(state, choice='root')
        state = self.advance(state, choice='newton')
        for value in (True, 'nan', 'inf', None, '1e900'):
            response = self.call('practice', action='check', id=state['id'], step=2, x0=value)
            self.assertEqual(response.status_code, 400, value)
            self.assertFalse(response.json()['success'])

    def test_new_pages_are_accessible_and_personal_links_are_secondary(self):
        for path in ('teoria', 'practica', 'autoevaluacion'):
            response = self.client.get(f'/ecuaciones-no-lineales/{path}/', follow=True)
            self.assertEqual(response.status_code, 200)
        html = response.content.decode()
        primary = html.split('class="primary-learning"', 1)[1].split('</nav>', 1)[0]
        self.assertNotIn('Mis apuntes', primary)
        self.assertNotIn('Mi progreso', primary)
        self.assertIn('Autoevaluación', primary)

    def test_conversational_search_finds_newton(self):
        response = self.client.get('/buscar/', {'q': 'Quiero Newton'})
        self.assertContains(response, '/ecuaciones-no-lineales/newton/')

    def test_repeating_a_practice_changes_its_data(self):
        original = self.start('newton')
        repeated = self.start('newton')
        self.assertNotEqual(original['id'], repeated['id'])
        self.assertNotEqual(original['expression'], repeated['expression'])
        self.assertEqual(repeated['step'], 0)

    def test_screenshot_case_identifies_each_error_and_accepts_equality(self):
        state = learning.start_practice('errores')
        state.update(variant=2, step=4, values={'x': .5})
        wrong = learning.check_practice(state, {'id': state['id'], 'step': 4, 'relative': .5, 'percentage': .2, 'decision': 'no'})
        self.assertFalse(wrong['correct'])
        self.assertEqual([item['correct'] for item in wrong['checks']], [False, False, False])
        self.assertIn('repetido el error absoluto', wrong['checks'][0]['message'])
        self.assertIn('igualdad', wrong['checks'][2]['message'])
        self.assertIn(r'\frac{0.5}{|20|}', wrong['checks'][0]['formula']['tex'])
        partial = learning.check_practice(state, {'id': state['id'], 'step': 4, 'relative': .025, 'percentage': .2, 'decision': 'yes'})
        self.assertEqual([item['correct'] for item in partial['checks']], [True, False, True])
        self.assertEqual(state['step'], 4)
        correct = learning.check_practice(state, {'id': state['id'], 'step': 4, 'relative': .025, 'percentage': 2.5, 'decision': 'yes'})
        self.assertTrue(correct['correct'])
        self.assertTrue(correct['state']['done'])
        self.assertEqual(correct['state']['verdict'], 'Cumple la tolerancia')
        self.assertEqual(correct['state']['results'][1]['fallback'], 'Er = 0.025')

    def test_error_checks_handle_negative_reference_and_percent_mixups(self):
        state = learning.start_practice('errores')
        state.update(variant=1, step=4, values={'x': .1})
        wrong = learning.check_practice(state, {'id': state['id'], 'step': 4, 'relative': 2, 'percentage': .02, 'decision': 'yes'})
        self.assertIn('porcentaje', wrong['checks'][0]['message'])
        self.assertIn('multiplicarla por 100', wrong['checks'][1]['message'])
        correct = learning.check_practice(state, {'id': state['id'], 'step': 4, 'relative': .02, 'percentage': 2, 'decision': 'no'})
        self.assertTrue(correct['correct'])

    def test_public_error_step_gives_formula_without_final_answers(self):
        state = learning.start_practice('errores')
        state.update(variant=2, step=4, values={'x': .5})
        public = learning.public_practice(state)
        self.assertEqual(len(public['math_context']['given']), 3)
        self.assertEqual(public['math_context']['known']['tex'], 'E_a=0.5')
        self.assertIn(r'\frac{E_a}{|v|}', public['fields'][0]['formula']['tex'])
        self.assertNotIn('results', public)

    @staticmethod
    def evaluate(expression, x):
        """Evaluación independiente del corrector: Python puro, sin pasar por el analizador de la aplicación."""
        env = {'exp': math.exp, 'cos': math.cos, 'sin': math.sin, 'sqrt': math.sqrt, 'x': x}
        return eval(expression.replace('^', '**'), {'__builtins__': {}}, env)

    def derivative(self, expression, x, order=1, h=1e-4):
        f = lambda t: self.evaluate(expression, t)
        if order == 1:
            return (f(x + h) - f(x - h)) / (2 * h)
        return (f(x + h) - 2 * f(x) + f(x - h)) / (h * h)

    def test_every_catalog_exercise_completes_with_independent_first_step_answers(self):
        from decimal import Decimal
        from .practice_bank import catalog, METHOD_KEYS, exercise_case
        self.assertEqual(len(catalog()), 54)
        for exercise in catalog():
            with self.subTest(exercise=exercise['id']):
                cache.clear()
                state = self.call('practice', action='start', topic=exercise['topic'], exercise=exercise['id']).json()
                choices = [value for value, _ in state['choices']]
                self.assertEqual(sorted(choices), sorted(['error', 'root', 'linear']))
                state = self.advance(state, choice='error' if state['topic'] == 'errores' else 'root')
                topic = state['topic']
                state = self.advance(state, choice='absolute' if topic == 'errores' else METHOD_KEYS[topic])
                case = exercise_case(self.client.session['learning_practice'])
                self.assertGreater(len(case['context']), 80)  # todo ejercicio trae un enunciado contextualizado
                if topic == 'errores':
                    ea = float(abs(Decimal(str(case['v'])) - Decimal(str(case['approx']))))
                    state = self.advance(state, v=case['v'], approx=case['approx'])
                    state = self.advance(state, x=ea)
                    state = self.advance(state, relative=ea/abs(case['v']) if case['v'] else 'undefined', percentage=100*ea/abs(case['v']) if case['v'] else 'undefined', decision='yes' if ea <= case['tolerance'] else 'no')
                else:
                    expression = case['expression']
                    f = lambda x: self.evaluate(expression, x)
                    if topic == 'punto-fijo':
                        x0 = case['low'] + .3 * (case['high'] - case['low'])
                        initial, x = dict(x0=x0), f(x0)
                        bound, residual = abs(x - x0), abs(f(x) - x)
                    elif topic == 'raices-multiples':
                        x0 = case['r'] + .5
                        df, ddf = self.derivative(expression, x0), self.derivative(expression, x0, 2)
                        initial = dict(x0=x0)
                        x = x0 - f(x0) * df / (df * df - f(x0) * ddf)
                        bound, residual = abs(x - x0), abs(f(x))
                    elif topic in ('biseccion', 'regla-falsa'):
                        initial = dict(a=0, b=4)
                        x = 2 if topic == 'biseccion' else -f(0) * 4 / (f(4) - f(0))
                        bound, residual = 2, abs(f(x))
                    elif topic == 'secante':
                        initial = dict(x0=.5, x1=2)
                        x = 2 - f(2) * 1.5 / (f(2) - f(.5))
                        bound, residual = abs(x - 2), abs(f(x))
                    else:
                        initial = dict(x0=1.5)
                        x = 1.5 - f(1.5) / self.derivative(expression, 1.5)
                        bound, residual = abs(x - 1.5), abs(f(x))
                    state = self.advance(state, **initial)
                    self.assertNotIn('results', state)
                    state = self.advance(state, x=x)
                    if topic == 'regla-falsa':
                        a, b = (x, x) if f(x) == 0 else (0, x) if f(0) * f(x) < 0 else (x, 4)
                        state = self.advance(state, new_a=a, new_b=b, residual=residual)
                    else:
                        state = self.advance(state, bound=bound, residual=residual)
                self.assertTrue(state['done'])

    def test_exercise_selection_is_validated_and_account_links_are_absent(self):
        for exercise in (True, [], 'newton-999', 'biseccion-0'):
            self.assertEqual(self.call('practice', action='start', topic='newton', exercise=exercise).status_code, 400)
        response = self.client.get('/ecuaciones-no-lineales/newton/')
        for removed in ('Ingresar', 'Mi progreso', 'Mis apuntes', 'Favoritos', 'complete-topic'):
            self.assertNotContains(response, removed)

    def test_secant_rejects_equal_images_and_false_position_checks_fields(self):
        state = self.call('practice', action='start', topic='secante', exercise='secante-0').json()
        state = self.advance(self.advance(state, choice='root'), choice='secant')
        self.assertFalse(self.answer(state, x0=1, x1=1)['correct'])
        state = self.call('practice', action='start', topic='regla-falsa', exercise='regla-falsa-0').json()
        state = self.advance(self.advance(state, choice='root'), choice='false-position')
        state = self.advance(state, a=0, b=2)
        state = self.advance(state, x=1)
        wrong = self.answer(state, new_a=0, new_b=2, residual=1)
        self.assertEqual([item['correct'] for item in wrong['checks']], [False, True, True])
        self.assertEqual(wrong['state']['step'], 4)

    def test_focused_pages_only_present_errors_and_preserve_secondary_catalog(self):
        self.assertRedirects(self.client.get('/ecuaciones-no-lineales/teoria/'), '/ecuaciones-no-lineales/errores/')
        response = self.client.get('/ecuaciones-no-lineales/practica/')
        self.assertEqual(len(response.context['exercises']), 15)
        self.assertTrue(response.context['errors_focus'])
        self.assertContains(response, 'id="practice-skill"')
        self.assertNotContains(response, 'data-start-topic="newton"')
        self.assertNotContains(response, 'data-start-topic="biseccion"')
        response = self.client.get('/ecuaciones-no-lineales/autoevaluacion/')
        self.assertContains(response, 'data-scope="modulo-1"')
        response = self.client.get('/ecuaciones-no-lineales/practica/?tema=newton')
        self.assertFalse(response.context['errors_focus'])
        self.assertContains(response, 'data-start-topic="newton"')

    def test_focused_sessions_do_not_resume_a_mixed_quiz_or_another_topic(self):
        original = self.start('newton')
        self.assertTrue(self.call('practice', action='resume', scope='errores').json()['empty'])
        self.assertEqual(self.call('practice', action='start', scope='errores', topic='newton').status_code, 400)
        focused = self.call('practice', action='start', scope='errores', topic='errores', exercise='errores-0').json()
        self.assertEqual(self.call('practice', action='resume').json()['id'], original['id'])
        self.assertEqual(self.call('practice', action='resume', scope='errores').json()['id'], focused['id'])
        self.assertEqual(self.call('practice', action='check', scope='errores', id=original['id'], step=0, choice='root').status_code, 400)

    def test_zero_reference_checks_undefined_measures_and_absolute_tolerance(self):
        state = self.call('practice', action='start', topic='errores', exercise='errores-9').json()
        state = self.advance(self.advance(state, choice='error'), choice='absolute')
        state = self.advance(state, v=0, approx=.0002)
        state = self.advance(state, x=.0002)
        self.assertTrue(state['reference_zero'])
        self.assertTrue(all('options' in field for field in state['fields']))
        wrong = self.answer(state, relative='zero', percentage='undefined', decision='no')
        self.assertEqual([check['correct'] for check in wrong['checks']], [False, True, True])
        self.assertIn('dividir entre cero', wrong['checks'][0]['message'])
        state = self.advance(state, relative='undefined', percentage='undefined', decision='no')
        self.assertEqual(state['results'][1]['fallback'], 'Er no definido')
        self.assertEqual(state['verdict'], 'No cumple la tolerancia')
        self.assertIn('/autoevaluacion/', state['next_url'])

    def test_explorer_accepts_decimal_boundaries_without_accepting_outside_values(self):
        for reference, approximation, tolerance in [('1', '1.1', '.1'), ('100', '99.95', '.05'), ('.1', '.3', '.2'), ('1e12', '-1e12', '2e12')]:
            result = self.client.post('/api/nonlinear/errors/', dict(true_value=reference, approximate_value=approximation, tolerance=tolerance), content_type='application/json').json()
            self.assertEqual(result['absolute'], float(tolerance))
            self.assertTrue(result['accepted'])
        result = self.client.post('/api/nonlinear/errors/', dict(true_value=1, approximate_value='1.100001', tolerance='.1'), content_type='application/json').json()
        self.assertFalse(result['accepted'])
        self.assertEqual(self.client.post('/api/nonlinear/errors/', dict(true_value=1, approximate_value=1, tolerance=-1), content_type='application/json').status_code, 400)


class PracticeLockTests(GuidedLearningTests):
    """Bloqueo al salir de la página, repetición desde el inicio, mezcla de opciones y enunciados contextualizados."""

    def leave(self, state, **extra):
        return self.call('practice', action='leave', id=state['id'], **extra)

    def test_leaving_locks_the_practice_and_reload_cannot_resume_it(self):
        state = self.start('errores')
        state = self.advance(state, choice='error')
        response = self.leave(state)
        self.assertEqual(response.status_code, 200)
        self.assertTrue(response.json()['locked'])
        resumed = self.call('practice', action='resume').json()          # equivale a recargar la página
        self.assertTrue(resumed['locked'])
        self.assertNotIn('fields', resumed)
        self.assertNotIn('choices', resumed)
        self.assertNotIn('math_context', resumed)
        self.assertIn('repetirla desde el inicio', resumed['message'])

    def test_a_locked_practice_rejects_answers(self):
        state = self.start('errores')
        self.leave(state)
        rejected = self.call('practice', action='check', id=state['id'], step=0, choice='error')
        self.assertEqual(rejected.status_code, 400)
        self.assertIn('bloqueada', rejected.json()['error'])

    def test_restart_repeats_the_same_exercise_from_step_zero(self):
        state = self.start('errores')
        state = self.advance(state, choice='error')
        state = self.advance(state, choice='absolute')
        self.leave(state)
        fresh = self.call('practice', action='restart').json()
        self.assertFalse(fresh.get('locked'))
        self.assertEqual(fresh['step'], 0)
        self.assertEqual(fresh['exercise'], state['exercise'])
        self.assertNotEqual(fresh['id'], state['id'])
        self.assertEqual(fresh['mistakes'], 0)
        self.assertEqual(self.call('practice', action='check', id=state['id'], step=2, v=1, approx=1).status_code, 400)  # estado viejo

    def test_lock_counter_survives_restart(self):
        state = self.start('newton')
        self.leave(state)
        fresh = self.call('practice', action='restart').json()
        self.leave(fresh)
        self.assertEqual(self.call('practice', action='resume').json()['locks'], 2)

    def test_leaving_is_idempotent_and_stale_notices_are_ignored(self):
        state = self.start('errores')
        self.leave(state)
        self.leave(state)
        self.assertEqual(self.call('practice', action='resume').json()['locks'], 1)
        fresh = self.call('practice', action='restart').json()
        stale = self.leave(state)  # aviso rezagado de la práctica anterior
        self.assertTrue(stale.json().get('ignored'))
        self.assertFalse(self.call('practice', action='resume').json().get('locked'))
        self.assertEqual(self.call('practice', action='resume').json()['id'], fresh['id'])

    def test_finished_practice_is_not_locked_when_leaving(self):
        state = learning.start_practice('errores')
        state.update(step=5, values={'x': .2})
        learning.lock_practice(state)
        self.assertFalse(state['locked'])

    def test_leave_without_a_practice_is_harmless(self):
        self.assertTrue(self.call('practice', action='leave').json()['empty'])
        self.assertEqual(self.call('practice', action='restart').status_code, 400)

    def test_lock_is_per_scope_in_the_session(self):
        original = self.start('newton')
        focused = self.call('practice', action='start', scope='errores', topic='errores', exercise='errores-0').json()
        self.call('practice', action='leave', scope='errores', id=focused['id'])
        self.assertTrue(self.call('practice', action='resume', scope='errores').json()['locked'])
        self.assertFalse(self.call('practice', action='resume').json().get('locked'))
        self.assertEqual(self.call('practice', action='resume').json()['id'], original['id'])

    def test_choice_order_is_shuffled_between_attempts_but_stable_on_reload(self):
        orders = set()
        for _ in range(25):
            state = self.call('practice', action='start', topic='errores', exercise='errores-0').json()
            again = self.call('practice', action='resume').json()
            self.assertEqual(state['choices'], again['choices'])             # estable al recargar
            orders.add(tuple(value for value, _ in state['choices']))
            cache.clear()
        self.assertGreater(len(orders), 2)
        self.assertTrue(all(sorted(order) == ['error', 'linear', 'root'] for order in orders))

    def test_every_exercise_has_a_contextualised_statement_with_its_numbers(self):
        from .practice_bank import catalog
        for exercise in catalog():
            context = exercise['context']
            self.assertGreater(len(context.split()), 18, exercise['id'])
            if exercise['topic'] == 'errores':
                self.assertRegex(context, r'[A-Za-zÁ-ú]{4,}')
        state = learning.start_practice('errores', exercise='errores-9')
        public = learning.public_practice(state)
        self.assertIn('presión', public['context_note'])
        state = learning.start_practice('newton', exercise='newton-3')
        self.assertIn('tanque', learning.public_practice(state)['problem'])

    def test_exercise_cards_show_the_story(self):
        response = self.client.get('/ecuaciones-no-lineales/practica/')
        self.assertContains(response, 'Pesa patrón en la balanza')
        self.assertContains(response, 'balanza de laboratorio')
        self.assertContains(response, 'Práctica individual')
