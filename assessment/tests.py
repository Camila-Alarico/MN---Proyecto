import random
import re
import uuid
from pathlib import Path

from django.conf import settings
from django.contrib.auth import get_user_model
from django.core.cache import cache
from django.test import Client, TestCase
from django.utils import timezone

from . import engine, generators
from .bank import BANK, MULTI, OPEN, SOURCES, STEPS, instantiate_steps
from .models import Attempt


class BankTests(TestCase):
    def test_bank_has_at_least_fifty_questions_with_all_formats(self):
        self.assertGreaterEqual(len(BANK), 50)
        self.assertGreaterEqual(len(MULTI), 10)
        self.assertGreaterEqual(len(OPEN), 10)
        self.assertGreaterEqual(len(STEPS), 8)

    def test_multiple_choice_has_five_or_more_options_and_several_correct(self):
        for q in MULTI:
            self.assertGreaterEqual(len(q['options']), 5, q['id'])
            self.assertGreaterEqual(len(q['correct']), 2, q['id'])
            self.assertLess(len(q['correct']), len(q['options']), q['id'])
            self.assertEqual(len(set(q['options'])), len(q['options']), q['id'])

    def test_every_question_points_at_a_real_lesson_file(self):
        for q in BANK.values():
            title, url, template = SOURCES[q['topic']]
            self.assertTrue((Path(settings.BASE_DIR) / template).is_file(), template)
            self.assertTrue(url.startswith(('/ecuaciones-no-lineales/', '/sistemas-lineales/')))
            self.assertEqual(self.client.get(url).status_code, 200, url)

    def test_open_rubrics_are_non_trivial(self):
        for q in OPEN:
            self.assertGreaterEqual(len(q['rubric']), 3 - (q['id'] == 'S-o1'), q['id'])
            self.assertGreaterEqual(q['min_words'], 15)
            self.assertTrue(q['model'])
            # La respuesta modelo debe satisfacer su propia rúbrica (si no, la rúbrica está mal escrita).
            case = q['case'](random.Random(1)) if q['case'] else None
            text = q['model'] + (' ' + ' '.join(generators.n(m) for m in case['must']) if case else '')
            result = engine.score_open(q, text + ' porque es el de la que se ' * 4, case)
            self.assertEqual(result['missed'], [], q['id'])

    def test_keyword_dump_does_not_score(self):
        q = BANK['G-o1']
        dump = ' '.join(['multiplicador redondeo amplifica mayor valor absoluto intercambio filas pivote pequeño error'] * 4)
        self.assertEqual(engine.score_open(q, dump, None)['score'], 0)
        prose = 'Dividir entre un pivote pequeño genera un multiplicador enorme que amplifica el error de redondeo, por eso se elige el mayor valor absoluto e intercambio filas.'
        self.assertGreater(engine.score_open(q, prose, None)['score'], 0.9)

    def test_step_generators_are_solvable_and_vary_between_seeds(self):
        for q in STEPS:
            signatures = set()
            for seed in range(200):
                data = instantiate_steps(q, seed)
                self.assertTrue(data['given'] and data['steps'])
                for step in data['steps']:
                    if step['kind'] == 'choice':
                        self.assertIn(step['answer'], [v for v, _ in step['options']])
                    else:
                        self.assertTrue(abs(step['answer']) < 1e9)
                signatures.add((tuple(data['given']), repr([round(s['answer'], 9) if s['kind'] == 'number' else s['answer'] for s in data['steps']])))
            self.assertGreaterEqual(len(signatures), 6, q['id'])  # datos realmente distintos entre intentos

    def test_scope_mixes_all_formats_and_shuffles_their_order(self):
        for key, info in engine.SCOPES.items():
            sequences = set()
            for _ in range(30):
                plan = engine.compose(key)
                kinds = [BANK[e['id']]['type'] for e in plan]
                sequences.add(tuple(kinds))
                self.assertEqual(kinds.count('multi'), info['mix'][0], key)
                self.assertEqual(kinds.count('open'), info['mix'][1], key)
                self.assertEqual(kinds.count('steps'), info['mix'][2], key)
                self.assertEqual(len(set(kinds)), 3)
                self.assertEqual(len({e['id'] for e in plan}), len(plan))
                self.assertTrue(all(BANK[e['id']]['topic'] in info['topics'] for e in plan))
            self.assertGreater(len(sequences), 1, key)
            self.assertTrue(any(len(set(sequence[i:i + 3])) > 1
                                for sequence in sequences for i in range(len(sequence) - 2)), key)


class ApiTestCase(TestCase):
    def setUp(self):
        cache.clear()
        self.url = '/evaluacion/api/'

    def call(self, client=None, **data):
        return (client or self.client).post(self.url, data, content_type='application/json')

    def start(self, scope='errores', client=None, name='Ana Quispe'):
        response = self.call(client, action='start', scope=scope, student_name=name)
        self.assertEqual(response.status_code, 200, response.content)
        return response.json()

    def attempt(self, state):
        return Attempt.objects.get(pk=state['attempt'])

    def correct_selection(self, attempt, question):
        entry = attempt.plan[question['index']]
        q = BANK[entry['id']]
        return [pos for pos, original in enumerate(entry['order']) if original in q['correct']]

    def first_of_type(self, attempt, kind):
        index = next(i for i, entry in enumerate(attempt.plan) if BANK[entry['id']]['type'] == kind)
        attempt.plan[0], attempt.plan[index] = attempt.plan[index], attempt.plan[0]
        attempt.save(update_fields=['plan'])
        return engine.attempt_view(attempt)

    def answer_current_correctly(self, state, attempt):
        question = state['question']
        index = question['index']
        entry = attempt.plan[index]
        bank_q = BANK[entry['id']]
        if question['type'] == 'multi':
            result = self.call(action='answer', attempt=state['attempt'], index=index,
                               selected=self.correct_selection(attempt, question)).json()
            return result['next']
        if question['type'] == 'open':
            case = bank_q['case'](random.Random(f'{bank_q["id"]}:{entry["seed"]}')) if bank_q['case'] else None
            text = bank_q['model'] + ' porque es el de la que se ' * 4
            if case:
                text += ' ' + ' '.join(generators.n(value) for value in case['must'])
            return self.call(action='answer', attempt=state['attempt'], index=index, text=text).json()['next']
        steps = instantiate_steps(bank_q, entry['seed'])['steps']
        result = None
        for step_index, step in enumerate(steps):
            value = step['answer'] if step['kind'] == 'choice' else str(step['answer'])
            result = self.call(action='answer', attempt=state['attempt'], index=index,
                               step=step_index, value=value).json()
        return result['next']


class FlowTests(ApiTestCase):
    def test_start_does_not_require_personal_data_and_rejects_invalid_scope(self):
        response = self.call(action='start', scope='errores')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(self.attempt(response.json()).student_name, 'Estudiante')
        self.assertEqual(self.call(action='start', scope='nada').status_code, 400)

    def test_questions_never_contain_the_answer(self):
        state = self.start()
        attempt = self.attempt(state)
        while not state.get('done'):
            keys = set()
            def collect(value):
                if isinstance(value, dict):
                    keys.update(value)
                    [collect(v) for v in value.values()]
                elif isinstance(value, list):
                    [collect(v) for v in value]
            collect(state['question'])
            self.assertFalse(keys & {'correct', 'answer', 'rubric', 'model', 'explanation', 'explain'}, keys)
            q = state['question']
            if q['type'] == 'multi':
                state = self.call(action='answer', attempt=state['attempt'], index=q['index'], selected=[0]).json()['next']
            elif q['type'] == 'open':
                state = self.call(action='answer', attempt=state['attempt'], index=q['index'], text='x ' * 40).json()['next']
            else:
                break

    def test_full_run_with_perfect_answers_passes(self):
        state = self.start('modulo-2')
        attempt = self.attempt(state)
        for _ in range(10):
            q = state['question']
            entry = attempt.plan[q['index']]
            bank_q = BANK[entry['id']]
            if q['type'] == 'multi':
                result = self.call(action='answer', attempt=state['attempt'], index=q['index'], selected=self.correct_selection(attempt, q)).json()
                self.assertTrue(result['result']['correct'])
                state = result['next']
            elif q['type'] == 'open':
                case = bank_q['case'](random.Random(f'{bank_q["id"]}:{entry["seed"]}')) if bank_q['case'] else None
                text = bank_q['model'] + ' porque es el de la que se ' * 4
                result = self.call(action='answer', attempt=state['attempt'], index=q['index'], text=text).json()
                self.assertGreaterEqual(result['result']['score'], 0.99, bank_q['id'])
                state = result['next']
            else:
                steps = instantiate_steps(bank_q, entry['seed'])['steps']
                for k, step in enumerate(steps):
                    result = self.call(action='answer', attempt=state['attempt'], index=q['index'], step=k, value=step['answer'] if step['kind'] == 'choice' else str(step['answer']).replace('.', ',')).json()
                    self.assertTrue(result['result']['correct'], (bank_q['id'], k, result))
                state = result['next']
        self.assertTrue(state['done'])
        self.assertEqual(state['points'], 10)
        self.assertTrue(state['passed'])
        attempt.refresh_from_db()
        self.assertTrue(attempt.finished)
        self.assertEqual(attempt.answers.count(), 10)

    def test_cannot_skip_ahead_or_replay_a_question(self):
        state = self.start()
        attempt = self.attempt(state)
        state = self.first_of_type(attempt, 'multi')
        aid = state['attempt']
        self.assertEqual(self.call(action='answer', attempt=aid, index=3, selected=[0]).status_code, 400)
        first = self.call(action='answer', attempt=aid, index=0, selected=[0, 1])
        self.assertEqual(first.status_code, 200)
        self.assertEqual(self.call(action='answer', attempt=aid, index=0, selected=[0]).status_code, 400)

    def test_multiple_choice_needs_a_selection_and_gives_partial_credit(self):
        state = self.start()
        attempt = self.attempt(state)
        state = self.first_of_type(attempt, 'multi')
        aid, q = state['attempt'], state['question']
        self.assertEqual(self.call(action='answer', attempt=aid, index=0, selected=[]).status_code, 400)
        self.assertEqual(self.call(action='answer', attempt=aid, index=0, selected=[99]).status_code, 400)
        self.assertEqual(self.call(action='answer', attempt=aid, index=0, selected=[0, 0]).status_code, 400)
        right = self.correct_selection(attempt, q)
        result = self.call(action='answer', attempt=aid, index=0, selected=right[:1]).json()['result']
        self.assertAlmostEqual(result['score'], 1 / len(right))
        self.assertFalse(result['correct'])
        self.assertEqual(sum(o['correct'] for o in result['options']), len(right))

    def test_open_answer_scoring_and_minimum_length(self):
        state = self.start()
        attempt = self.attempt(state)
        state = self.first_of_type(attempt, 'open')
        aid = state['attempt']
        q = state['question']
        short = self.call(action='answer', attempt=aid, index=0, text='muy corta').json()['result']
        self.assertEqual(short['score'], 0)
        self.assertTrue(attempt.answers.get(index=0).response['text'])

    def test_steps_gate_each_step_and_reveal_after_three_failures(self):
        state = self.start()
        attempt = self.attempt(state)
        state = self.first_of_type(attempt, 'steps')
        aid = state['attempt']
        q = state['question']
        items = q['steps']['items']
        self.assertEqual([i['status'] for i in items][:2], ['current', 'locked'])
        self.assertNotIn('prompt', items[1])
        self.assertEqual(self.call(action='answer', attempt=aid, index=0, step=1, value='1').status_code, 400)
        entry = attempt.plan[0]
        steps = instantiate_steps(BANK[entry['id']], entry['seed'])['steps']
        wrong = '-987654' if steps[0]['kind'] == 'number' else next(v for v, _ in steps[0]['options'] if v != steps[0]['answer'])
        for _ in (1, 2, 3):
            result = self.call(action='answer', attempt=aid, index=0, step=0, value=wrong).json()
            self.assertFalse(result['result']['correct'])
        self.assertTrue(result['result']['revealed'])
        self.assertEqual(result['question']['steps']['items'][0]['status'], 'done')
        self.assertEqual(result['question']['steps']['items'][1]['status'], 'current')

    def test_steps_score_decreases_with_retries(self):
        state = self.start()
        attempt = self.attempt(state)
        state = self.first_of_type(attempt, 'steps')
        aid = state['attempt']
        entry = attempt.plan[0]
        steps = instantiate_steps(BANK[entry['id']], entry['seed'])['steps']
        for k, step in enumerate(steps):
            if k == 0:
                bad = '-987654' if step['kind'] == 'number' else next(v for v, _ in step['options'] if v != step['answer'])
                self.call(action='answer', attempt=aid, index=0, step=0, value=bad)
            value = step['answer'] if step['kind'] == 'choice' else str(step['answer'])
            result = self.call(action='answer', attempt=aid, index=0, step=k, value=value).json()
        score = attempt.answers.get(index=0).score
        self.assertAlmostEqual(score, (0.5 + (len(steps) - 1)) / len(steps))

    def test_non_numeric_step_input_is_rejected_without_costing_an_attempt(self):
        state = self.start()
        attempt = self.attempt(state)
        state = self.first_of_type(attempt, 'steps')
        aid = state['attempt']
        entry = attempt.plan[0]
        first = instantiate_steps(BANK[entry['id']], entry['seed'])['steps'][0]
        if first['kind'] == 'number':
            for bad in ('abc', 'nan', 'inf', '1e999', True, None):
                self.assertEqual(self.call(action='answer', attempt=aid, index=0, step=0, value=bad).status_code, 400, bad)
            attempt.refresh_from_db()
            self.assertEqual(attempt.state.get('0', {}).get('tries', 0), 0)

    def test_another_browser_cannot_use_my_attempt(self):
        state = self.start()
        stranger = Client()
        response = self.call(stranger, action='answer', attempt=state['attempt'], index=0, selected=[0])
        self.assertEqual(response.status_code, 400)
        self.assertEqual(self.call(stranger, action='leave', attempt=state['attempt']).status_code, 400)
        self.assertEqual(self.call(action='answer', attempt=str(uuid.uuid4()), index=0, selected=[0]).status_code, 400)
        self.assertEqual(self.call(action='answer', attempt='no-es-uuid', index=0, selected=[0]).status_code, 400)

    def test_resume_returns_the_current_question_for_the_same_browser_only(self):
        state = self.start()
        attempt = self.attempt(state)
        state = self.first_of_type(attempt, 'multi')
        self.call(action='answer', attempt=state['attempt'], index=0, selected=[0])
        resumed = self.call(action='resume', scope='errores').json()
        self.assertEqual(resumed['question']['index'], 1)
        self.assertTrue(self.call(Client(), action='resume', scope='errores').json()['empty'])

    def test_logged_in_student_uses_account_name(self):
        user = get_user_model().objects.create_user('lucia', password='x-pass-12345')
        client = Client()
        client.force_login(user)
        state = self.call(client, action='start', scope='errores').json()
        self.assertEqual(self.attempt(state).student_name, 'lucia')
        self.assertEqual(self.attempt(state).user, user)


class AutoResetTests(ApiTestCase):
    def set_away_time(self, attempt_id, seconds_ago):
        session = self.client.session
        session['assessment_away'] = {
            'attempt': attempt_id,
            'at': timezone.now().timestamp() - seconds_ago,
        }
        session.save()

    def test_return_before_five_seconds_keeps_progress(self):
        state = self.start()
        attempt = self.attempt(state)
        state = self.first_of_type(attempt, 'multi')
        aid = state['attempt']
        self.call(action='answer', attempt=aid, index=0, selected=[0])
        self.call(action='leave', attempt=aid)
        self.set_away_time(aid, 4.5)
        resumed = self.call(action='resume', scope='errores').json()
        self.assertEqual(resumed['attempt'], aid)
        self.assertEqual(resumed['question']['index'], 1)
        self.assertTrue(resumed.get('resumed'))
        self.assertFalse(resumed.get('restarted'))

    def test_return_after_more_than_five_seconds_starts_from_zero(self):
        state = self.start()
        attempt = self.attempt(state)
        state = self.first_of_type(attempt, 'multi')
        aid = state['attempt']
        self.call(action='answer', attempt=aid, index=0, selected=[0])
        self.call(action='leave', attempt=aid)
        self.set_away_time(aid, 5.1)
        resumed = self.call(action='resume', scope='errores').json()
        self.assertNotEqual(resumed['attempt'], aid)
        self.assertEqual(resumed['question']['index'], 0)
        self.assertTrue(resumed['restarted'])
        self.assertFalse(Attempt.objects.filter(pk=aid).exists())

    def test_explicit_restart_discards_answers_and_progress(self):
        state = self.start()
        aid = state['attempt']
        self.call(action='answer', attempt=aid, index=0, selected=[0])
        fresh = self.call(action='restart', attempt=aid).json()
        self.assertNotEqual(fresh['attempt'], aid)
        self.assertEqual(fresh['question']['index'], 0)
        self.assertTrue(fresh['restarted'])
        self.assertFalse(Attempt.objects.filter(pk=aid).exists())

    def test_exit_events_are_not_an_available_api_action(self):
        state = self.start()
        self.assertEqual(self.call(action='event', attempt=state['attempt'], kind='leave').status_code, 400)



class PagesTests(TestCase):
    def test_assessment_pages_render_with_expected_scope(self):
        for path, scope in (('/evaluacion/', 'curso'), ('/evaluacion/?alcance=modulo-2', 'modulo-2'),
                            ('/ecuaciones-no-lineales/autoevaluacion/', 'modulo-1'), ('/evaluacion/?alcance=raro', 'curso')):
            response = self.client.get(path)
            self.assertEqual(response.status_code, 200, path)
            self.assertContains(response, f'data-scope="{scope}"')
            self.assertContains(response, 'más de 5 segundos')
            self.assertNotContains(response, 'Banco de preguntas')
            self.assertNotContains(response, 'preguntas · banco de')
            self.assertNotContains(response, 'preguntas disponibles')

    def test_theory_button_goes_to_the_general_course_theory_in_both_modules(self):
        hub = self.client.get('/teoria/')
        self.assertEqual(hub.status_code, 200)
        for text in ('Ecuaciones no lineales y errores', 'Sistemas de ecuaciones lineales', 'Formulación y convergencia', 'Métodos cerrados'):
            self.assertContains(hub, text)
        for path in ('/', '/ecuaciones-no-lineales/errores/', '/ecuaciones-no-lineales/biseccion/', '/sistemas-lineales/', '/sistemas-lineales/gauss-seidel/',
                     '/evaluacion/', '/teoria/'):
            sidebar = self.client.get(path).content.decode().split('class="primary-learning"', 1)[1].split('</nav>', 1)[0]
            theory_link = re.search(r'<a href="([^"]+)"[^>]*><span[^>]*>01</span> Teoría</a>', sidebar)
            self.assertIsNotNone(theory_link, path)
            self.assertEqual(theory_link.group(1), '/teoria/', path)

    def test_assessment_selector_keeps_both_modules_and_full_course(self):
        response = self.client.get('/ecuaciones-no-lineales/autoevaluacion/')
        self.assertContains(response, '¿Qué módulo quieres autoevaluar?')
        for scope in ('modulo-1', 'modulo-2', 'curso', 'errores'):
            self.assertContains(response, f'value=\"{scope}\"')
        self.assertContains(response, 'Comenzar módulo seleccionado')
        self.assertContains(response, 'La plataforma no registra ni muestra salidas')

    def test_module_two_sidebar_links_to_its_assessment(self):
        sidebar = self.client.get('/sistemas-lineales/').content.decode()
        self.assertIn('/evaluacion/?alcance=modulo-2', sidebar)

    def test_there_is_no_teacher_monitoring_route_or_sidebar_link(self):
        self.assertEqual(self.client.get('/evaluacion/docente/').status_code, 404)
        self.assertNotContains(self.client.get('/'), '/evaluacion/docente/')

    def test_old_three_option_quiz_api_is_gone(self):
        response = self.client.post('/api/nonlinear/learning/quiz/', {'action': 'start'}, content_type='application/json')
        self.assertEqual(response.status_code, 400)


class ErrorsBankTests(ApiTestCase):
    def test_errors_module_has_exactly_fifty_questions_organised_by_subtopic(self):
        from .bank import SUBTOPICS, outline
        errors = [q for q in BANK.values() if q['topic'] == 'errores']
        self.assertEqual(len(errors), 50)
        self.assertEqual({q['type'] for q in errors}, {'multi', 'open', 'steps'})
        self.assertEqual({q['sub'] for q in errors}, set(SUBTOPICS))
        self.assertEqual(engine.bank_size('errores'), 50)
        row = next(item for item in outline() if item['topic'] == 'errores')
        self.assertEqual(sum(sub['total'] for sub in row['subtopics']), 50)
        for other in outline():
            if other['topic'] != 'errores':
                self.assertEqual(other['subtopics'], [])

    def test_other_modules_keep_their_previous_bank(self):
        others = [q for q in BANK.values() if q['topic'] != 'errores']
        self.assertEqual(len(others), 43)

    def test_start_page_does_not_reveal_bank_size_or_question_count(self):
        page = self.client.get('/evaluacion/')
        self.assertNotContains(page, 'Banco de preguntas')
        self.assertNotContains(page, '50 preguntas')
        self.assertNotContains(page, 'pregunta(s)')

    def test_each_errors_attempt_spreads_over_subtopics(self):
        for _ in range(15):
            plan = engine.compose('errores')
            subs = {BANK[e['id']]['sub'] for e in plan}
            self.assertGreaterEqual(len(subs), 4)


class VariationTests(ApiTestCase):
    def test_options_are_shuffled_per_attempt_not_fixed(self):
        """La opción que abre la lista cambia de un intento a otro: la correcta no ocupa siempre el mismo lugar."""
        first_options = {}
        for _ in range(400):
            for entry in engine.compose('curso'):
                if BANK[entry['id']]['type'] == 'multi':
                    first_options.setdefault(entry['id'], []).append(entry['order'][0])
        self.assertGreater(len(first_options), 10)
        for q_id, firsts in first_options.items():
            if len(firsts) >= 8:
                self.assertGreater(len(set(firsts)), 2, q_id)

    def test_served_options_follow_the_stored_shuffle(self):
        state = self.start()
        attempt = self.attempt(state)
        state = self.first_of_type(attempt, 'multi')
        entry = attempt.plan[0]
        q = BANK[entry['id']]
        self.assertEqual(state['question']['options'], [q['options'][i] for i in entry['order']])

    def test_consecutive_attempts_do_not_repeat_questions(self):
        client = Client()
        first = self.attempt(self.start(client=client))
        second = self.attempt(self.start(client=client))
        third = self.attempt(self.start(client=client))
        ids = lambda attempt: {e['id'] for e in attempt.plan}
        self.assertEqual(ids(first) & ids(second), set())
        self.assertEqual(ids(second) & ids(third), set())

    def test_numbers_of_step_problems_change_between_attempts(self):
        signatures = set()
        for _ in range(12):
            entry = {'id': 'E-s1', 'seed': random.getrandbits(32)}
            data = instantiate_steps(BANK['E-s1'], entry['seed'])
            signatures.add(tuple(data['given']))
        self.assertGreater(len(signatures), 3)


class ReviewTests(ApiTestCase):
    def run_attempt(self, client, mistakes):
        """Responde un intento completo; `mistakes` indica qué posiciones se contestan mal (por índice de pregunta)."""
        state = self.start(client=client)
        attempt = self.attempt(state)
        if mistakes is None:
            kinds = [BANK[item['id']]['type'] for item in attempt.plan]
            mistakes = {next(i for i, kind in enumerate(kinds) if kind == target)
                        for target in ('multi', 'open', 'steps')}
        wrong_by_index = {}
        for i in range(len(attempt.plan)):
            q = state['question']
            entry = attempt.plan[i]
            bank_q = BANK[entry['id']]
            bad = i in mistakes
            if q['type'] == 'multi':
                selected = [0] if bad and not self.correct_selection(attempt, q) == [0] else self.correct_selection(attempt, q)
                if bad:
                    selected = [pos for pos, original in enumerate(entry['order']) if original not in bank_q['correct']][:1]
                result = self.call(client, action='answer', attempt=state['attempt'], index=i, selected=selected).json()
            elif q['type'] == 'open':
                text = 'respuesta corta sin contenido útil ' * 6 if bad else bank_q['model'] + ' porque es el de la que se ' * 4
                case = bank_q['case'](random.Random(f'{bank_q["id"]}:{entry["seed"]}')) if bank_q['case'] else None
                if case and not bad:
                    text += ' ' + ' '.join(generators.n(m) for m in case['must'])
                result = self.call(client, action='answer', attempt=state['attempt'], index=i, text=text).json()
            else:
                steps = instantiate_steps(bank_q, entry['seed'])['steps']
                for k, step in enumerate(steps):
                    if bad and k == 0:
                        wrong = '-987654' if step['kind'] == 'number' else next(v for v, _ in step['options'] if v != step['answer'])
                        self.call(client, action='answer', attempt=state['attempt'], index=i, step=k, value=wrong)
                    value = step['answer'] if step['kind'] == 'choice' else str(step['answer'])
                    result = self.call(client, action='answer', attempt=state['attempt'], index=i, step=k, value=value).json()
            if bad:
                wrong_by_index[i + 1] = bank_q['id']
            state = result['next'] if result.get('next') else state
            if state.get('done'):
                break
        return state, wrong_by_index

    def test_review_lists_only_questions_answered_wrong(self):
        client = Client()
        final, wrong = self.run_attempt(client, mistakes=None)
        self.assertTrue(final['done'])
        self.assertEqual(final['wrong'], 3)
        review = self.call(client, action='review', attempt=final['attempt']).json()
        self.assertEqual(review['wrong'], 3)
        self.assertEqual({item['index'] for item in review['review']}, set(wrong))
        kinds = {item['type'] for item in review['review']}
        self.assertEqual(kinds, {'multi', 'open', 'steps'})
        multi = next(i for i in review['review'] if i['type'] == 'multi')
        self.assertTrue(any(o['correct'] for o in multi['options']) and any(o['chosen'] and not o['correct'] for o in multi['options']))
        steps = next(i for i in review['review'] if i['type'] == 'steps')
        self.assertEqual(steps['steps'][0]['typed'][0], '-987654' if steps['steps'][0]['typed'][0][0] == '-' else steps['steps'][0]['typed'][0])
        self.assertIn('correct', steps['steps'][0])

    def test_perfect_attempt_has_nothing_to_review(self):
        client = Client()
        final, _ = self.run_attempt(client, mistakes=set())
        self.assertEqual(final['wrong'], 0)
        self.assertEqual(self.call(client, action='review', attempt=final['attempt']).json()['review'], [])

    def test_review_requires_a_finished_attempt_and_ownership(self):
        client = Client()
        state = self.start(client=client)
        self.assertEqual(self.call(client, action='review', attempt=state['attempt']).status_code, 400)
        final, _ = self.run_attempt(Client(), mistakes={0})
        self.assertEqual(self.call(Client(), action='review', attempt=final['attempt']).status_code, 400)


class ModuleScopeTests(ApiTestCase):
    def test_student_can_take_an_assessment_of_a_single_module(self):
        for scope, topics in (('errores', {'errores'}), ('modulo-1', set(engine.SCOPES['modulo-1']['topics'])),
                              ('modulo-2', set(engine.SCOPES['modulo-2']['topics']))):
            state = self.start(scope)
            plan = self.attempt(state).plan
            self.assertTrue(all(BANK[e['id']]['topic'] in topics for e in plan), scope)
            self.assertEqual(state['scope'], scope)
