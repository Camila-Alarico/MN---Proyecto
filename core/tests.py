"""Pruebas de cuentas, progreso, apuntes e historial (app core)."""
from django.contrib.auth.models import User
from django.core import mail
from django.test import TestCase
from django.urls import reverse

from nonlinear.models import CalculationHistory

from .models import StudyNote, UserProgress


class RegisterTests(TestCase):
    def test_register_requires_email_and_adopts_guest_progress(self):
        session = self.client.session
        session['completed_topics'] = ['conceptos', 'errores', 'tema-inexistente']
        session.save()
        response = self.client.post(
            reverse('register'),
            {'username': 'ana', 'email': 'ana@example.com', 'password1': 'Clave-segura-2026', 'password2': 'Clave-segura-2026'},
        )
        self.assertRedirects(response, '/')
        user = User.objects.get(username='ana')
        self.assertEqual(user.email, 'ana@example.com')
        topics = set(UserProgress.objects.filter(user=user, completed=True).values_list('topic', flat=True))
        self.assertEqual(topics, {'conceptos', 'errores'})
        self.assertNotIn('completed_topics', self.client.session)

    def test_register_without_email_fails(self):
        response = self.client.post(
            reverse('register'), {'username': 'ana', 'password1': 'Clave-segura-2026', 'password2': 'Clave-segura-2026'}
        )
        self.assertEqual(response.status_code, 200)
        self.assertFalse(User.objects.filter(username='ana').exists())

    def test_duplicate_email_rejected(self):
        User.objects.create_user('otro', 'ana@example.com', 'x')
        response = self.client.post(
            reverse('register'),
            {'username': 'ana', 'email': 'ANA@example.com', 'password1': 'Clave-segura-2026', 'password2': 'Clave-segura-2026'},
        )
        self.assertContains(response, 'Ya existe una cuenta con este correo')


class LoginProgressTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user('ana', 'ana@example.com', 'Clave-segura-2026')

    def test_login_adopts_guest_progress(self):
        session = self.client.session
        session['completed_topics'] = ['newton']
        session.save()
        self.client.post(reverse('login'), {'username': 'ana', 'password': 'Clave-segura-2026'})
        self.assertTrue(UserProgress.objects.filter(user=self.user, topic='newton', completed=True).exists())


class PasswordResetTests(TestCase):
    def test_reset_flow_sends_email(self):
        User.objects.create_user('ana', 'ana@example.com', 'Clave-segura-2026')
        response = self.client.post(reverse('password_reset'), {'email': 'ana@example.com'})
        self.assertRedirects(response, reverse('password_reset_done'))
        self.assertEqual(len(mail.outbox), 1)
        self.assertIn('/cuenta/recuperar/', mail.outbox[0].body)


class NotesTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user('ana', 'ana@example.com', 'x')
        self.other = User.objects.create_user('luis', 'luis@example.com', 'x')
        self.client.force_login(self.user)

    def test_create_and_delete_note(self):
        self.client.post(reverse('notes'), {'text': 'Bisección necesita cambio de signo.'})
        note = StudyNote.objects.get(user=self.user)
        response = self.client.post(reverse('delete-note', args=[note.pk]))
        self.assertRedirects(response, reverse('notes'))
        self.assertFalse(StudyNote.objects.filter(pk=note.pk).exists())

    def test_cannot_delete_another_users_note(self):
        note = StudyNote.objects.create(user=self.other, text='privado')
        response = self.client.post(reverse('delete-note', args=[note.pk]))
        self.assertEqual(response.status_code, 404)
        self.assertTrue(StudyNote.objects.filter(pk=note.pk).exists())


class HistoryTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user('ana', 'ana@example.com', 'x')
        self.other = User.objects.create_user('luis', 'luis@example.com', 'x')
        self.client.force_login(self.user)
        self.item = CalculationHistory.objects.create(
            user=self.user, method='newton', function_expression='x^2-2', parameters={'x0': 1},
            result={'root': 1.41421356, 'status': 'Convergió', 'converged': True, 'iterations_count': 4},
        )

    def test_progress_page_shows_topics_and_history(self):
        UserProgress.objects.create(user=self.user, topic='newton', completed=True, progress_percentage=100)
        response = self.client.get(reverse('progress'))
        self.assertContains(response, 'Newton-Raphson')
        self.assertContains(response, 'x^2-2')
        self.assertContains(response, 'Eliminar cálculo')

    def test_toggle_favorite_returns_to_origin(self):
        response = self.client.post(reverse('toggle-favorite', args=[self.item.pk]), {'next': reverse('favorites')})
        self.assertRedirects(response, reverse('favorites'))
        self.item.refresh_from_db()
        self.assertTrue(self.item.favorite)

    def test_delete_history_only_own(self):
        foreign = CalculationHistory.objects.create(user=self.other, method='newton', function_expression='x', parameters={}, result={})
        self.assertEqual(self.client.post(reverse('delete-history', args=[foreign.pk])).status_code, 404)
        response = self.client.post(reverse('delete-history', args=[self.item.pk]))
        self.assertRedirects(response, reverse('progress'))
        self.assertFalse(CalculationHistory.objects.filter(pk=self.item.pk).exists())

    def test_identical_consecutive_calculations_are_grouped(self):
        payload = {'expression': 'x^3 - x - 2', 'x0': 1.5, 'tolerance': 0.0001, 'max_iterations': 100}
        for _ in range(3):
            response = self.client.post('/api/nonlinear/newton/', payload, content_type='application/json')
            self.assertEqual(response.status_code, 200)
        self.assertEqual(CalculationHistory.objects.filter(user=self.user, method='newton', function_expression='x^3 - x - 2').count(), 1)


class NavigationTests(TestCase):
    def test_home_lists_modules_from_catalog_and_hides_fake_widgets(self):
        response = self.client.get('/')
        self.assertContains(response, 'Sistemas de ecuaciones lineales')
        self.assertContains(response, '2 de 5 módulos disponibles')
        self.assertNotContains(response, 'Sin notificaciones nuevas')
        self.assertNotContains(response, 'bi-lock')
        self.assertContains(response, 'integrity="sha384-')


class RevisionIntegrationTests(TestCase):
    def test_lesson_and_chapter_styles_survive_template_merge(self):
        response = self.client.get('/')
        for stylesheet in ('lessons.css', 'chapters.css', 'learning.css'):
            self.assertContains(response, '/static/css/' + stylesheet)

    def test_guest_completion_updates_an_existing_partial_record(self):
        user = User.objects.create_user('partial', 'partial@example.com', 'clave')
        progress = UserProgress.objects.create(user=user, topic='errores', progress_percentage=30)
        session = self.client.session
        session['completed_topics'] = ['errores']
        session.save()
        self.client.force_login(user)
        progress.refresh_from_db()
        self.assertTrue(progress.completed)
        self.assertEqual(progress.progress_percentage, 100)
        self.assertEqual(UserProgress.objects.filter(user=user, topic='errores').count(), 1)

    def test_reset_link_changes_password_and_cannot_be_reused(self):
        import re
        from urllib.parse import urlsplit
        user = User.objects.create_user('reset', 'reset@example.com', 'Anterior-segura-2026')
        self.client.post(reverse('password_reset'), {'email': user.email})
        link = re.search(r'https?://\S+', mail.outbox[0].body).group()
        response = self.client.get(urlsplit(link).path)
        confirmation = response.url
        response = self.client.post(confirmation, {'new_password1': 'Nueva-segura-2026', 'new_password2': 'Nueva-segura-2026'})
        self.assertRedirects(response, reverse('password_reset_complete'))
        user.refresh_from_db()
        self.assertTrue(user.check_password('Nueva-segura-2026'))
        self.assertContains(self.client.get(urlsplit(link).path), 'Enlace no válido')


class ConsolidatedRoutingTests(TestCase):
    """Verifica el mapa de rutas descrito en nonlinear/urls.py: una URL por contenido."""

    def test_legacy_lab_link_redirects_to_canonical_method_url(self):
        response = self.client.get('/ecuaciones-no-lineales/laboratorio/?method=newton&expression=x')
        self.assertRedirects(response, '/ecuaciones-no-lineales/newton/?expression=x', status_code=301, fetch_redirect_response=False)

    def test_legacy_lab_link_without_method_defaults_to_bisection(self):
        response = self.client.get('/ecuaciones-no-lineales/laboratorio/')
        self.assertRedirects(response, '/ecuaciones-no-lineales/biseccion/', status_code=301, fetch_redirect_response=False)

    def test_canonical_method_url_is_used_and_legacy_alias_is_not(self):
        response = self.client.get('/ecuaciones-no-lineales/teoria/?vista=modulo')
        self.assertContains(response, 'href="/ecuaciones-no-lineales/biseccion/"')
        self.assertNotContains(response, 'href="/ecuaciones-no-lineales/laboratorio/"')

    def test_guided_practice_replaces_removed_quiz_page(self):
        self.assertContains(self.client.get('/ecuaciones-no-lineales/practica/'), 'Práctica guiada')


class SearchConsolidationTests(TestCase):
    """La búsqueda, sin importar dónde se escriba, siempre resuelve en /buscar/."""

    def test_navbar_search_form_points_to_single_destination(self):
        response = self.client.get('/')
        self.assertContains(response, 'action="/buscar/"')

    def test_search_finds_topic_ignoring_accents_and_case(self):
        response = self.client.get(reverse('search'), {'q': 'BISECCION'})
        self.assertContains(response, 'Bisección')

    def test_search_finds_course_module(self):
        response = self.client.get(reverse('search'), {'q': 'gauss'})
        self.assertContains(response, 'Sistemas de ecuaciones lineales')

    def test_empty_query_shows_no_results(self):
        response = self.client.get(reverse('search'))
        self.assertNotContains(response, 'resultado')


class QuizRemovalTests(TestCase):
    def test_practica_topic_removed_from_sidebar(self):
        response = self.client.get('/')
        self.assertNotContains(response, '>Práctica<')

    def test_exercise_endpoints_are_gone(self):
        response = self.client.post(
            '/api/nonlinear/exercises/1/', {'answer': 'x'}, content_type='application/json',
        )
        self.assertEqual(response.status_code, 404)

    def test_challenge_and_experiment_endpoints_are_gone(self):
        for path, payload in (('/api/nonlinear/challenges/0/', {'method': 'newton', 'answer': 1.5}),
                              ('/api/nonlinear/experiments/family/', {'mu': .25})):
            response = self.client.post(path, payload, content_type='application/json')
            self.assertEqual(response.status_code, 404, path)


class ModuleSelectionNavigationTests(TestCase):
    """La navbar apunta a la selección de módulos (`/#modules`), generada desde core/catalog.py."""

    def test_navbar_links_to_module_selector_not_to_module_one(self):
        response = self.client.get('/ecuaciones-no-lineales/')
        self.assertContains(response, 'href="/#modules"')
        self.assertNotContains(response, 'ecuaciones-no-lineales/experimentos')
        self.assertNotContains(response, '>Experimentos<')

    def test_selector_lists_every_catalog_module(self):
        from .catalog import MODULES
        response = self.client.get('/')
        self.assertContains(response, 'id="modules"')
        for module in MODULES:
            self.assertContains(response, module['title'])
        self.assertContains(response, 'href="/sistemas-lineales/"')

    def test_removed_sections_are_gone(self):
        for url in ('/ecuaciones-no-lineales/experimentos/', '/ecuaciones-no-lineales/desafios/',
                    '/sistemas-lineales/ejercicios/'):
            self.assertEqual(self.client.get(url).status_code, 404, url)
        for url in ('/', '/ecuaciones-no-lineales/', '/sistemas-lineales/', '/ecuaciones-no-lineales/biseccion/',
                    '/ecuaciones-no-lineales/polinomios/', '/ecuaciones-no-lineales/errores/',
                    '/ecuaciones-no-lineales/conceptos/'):
            html = self.client.get(url).content.decode()
            for stale in ('/experimentos/', '/desafios/', '/ejercicios/'):
                self.assertNotIn(stale, html, f'{url} aún enlaza a {stale}')


class ComparisonTests(TestCase):
    """Recorridos, propagación de errores y convergencia/divergencia (comparar.html)."""

    def _compare(self, methods, **extra):
        payload = {
            'expression': 'x^3 - x - 2', 'a': 1, 'b': 2, 'x0': 1.5, 'x1': 2,
            'tolerance': 0.000001, 'max_iterations': 100, 'methods': methods, **extra,
        }
        response = self.client.post('/api/nonlinear/compare/', payload, content_type='application/json')
        self.assertEqual(response.status_code, 200, response.content)
        return response.json()

    def test_compare_returns_a_walk_per_method_with_error_against_reference(self):
        data = self._compare(['bisection', 'newton'])
        self.assertTrue(data['success'])
        self.assertAlmostEqual(data['reference']['root'], 1.5213797, places=5)
        for entry in data['methods']:
            self.assertTrue(entry['converged'])
            self.assertGreater(len(entry['rows']), 0)
            self.assertLess(entry['final']['absolute'], 1e-4)

    def test_newton_converges_faster_than_bisection_on_a_simple_root(self):
        data = self._compare(['bisection', 'newton'])
        by_key = {m['key']: m for m in data['methods']}
        self.assertLess(by_key['newton']['iterations_count'], by_key['bisection']['iterations_count'])
        self.assertEqual(by_key['newton']['convergence']['verdict'], 'converge')
        self.assertAlmostEqual(by_key['newton']['convergence']['lambda'], 0.0, places=3)

    def test_error_propagation_between_methods_is_reported(self):
        data = self._compare(['bisection', 'newton'])
        self.assertEqual(len(data['propagation']), 1)
        pair = data['propagation'][0]
        self.assertTrue(pair['consistent'])
        self.assertGreaterEqual(pair['bound'], pair['difference'])

    def test_divergent_fixed_point_transformation_is_flagged(self):
        # g(x) = x^3 - 2 no es una contracción cerca de la raíz: |g'(1.52)| = 3x^2 ~ 6.9 > 1.
        data = self._compare(['fixed-point'], g='x^3 - 2', x0=1.2)
        entry = data['methods'][0]
        self.assertEqual(entry['convergence']['verdict'], 'diverge')
        self.assertGreater(entry['convergence']['lambda'], 1)

    def test_bracketing_convergence_reports_sign_change_criterion(self):
        data = self._compare(['bisection'])
        conv = data['methods'][0]['convergence']
        self.assertEqual(conv['verdict'], 'converge')
        self.assertTrue(conv['checks'][0]['ok'])

    def test_unknown_method_is_rejected(self):
        response = self.client.post(
            '/api/nonlinear/compare/',
            {'expression': 'x', 'methods': ['not-a-method'], 'tolerance': 0.0001, 'max_iterations': 50},
            content_type='application/json',
        )
        self.assertEqual(response.status_code, 400)


class LearningRouteTests(TestCase):
    """La barra lateral muestra una ruta corta por módulo; los métodos se eligen dentro del simulador."""

    def test_module_one_route_has_six_steps_and_hides_individual_methods(self):
        response = self.client.get('/ecuaciones-no-lineales/teoria/?vista=modulo')
        for title in ('Errores numéricos', 'Raíces de ecuaciones', 'Métodos cerrados', 'Métodos abiertos',
                      'Raíces múltiples de polinomios', 'Comparar métodos'):
            self.assertContains(response, title)
        sidebar = response.content.decode().split('<aside', 1)[1].split('</aside>', 1)[0]
        for hidden in ('>Regla falsa', '>Punto fijo', '>Secante', '>Newton-Raphson', '>Bisección'):
            self.assertNotIn(hidden, sidebar)
        self.assertContains(response, 'href="/ecuaciones-no-lineales/biseccion/"')
        self.assertContains(response, 'href="/ecuaciones-no-lineales/newton/"')
        self.assertEqual(len(response.context['route_topics']), 6)

    def test_module_two_route_groups_direct_and_iterative(self):
        response = self.client.get('/')
        self.assertContains(response, 'Métodos directos')
        self.assertContains(response, 'Métodos iterativos')
        self.assertContains(response, 'href="/sistemas-lineales/gauss-seidel/"')

    def test_every_method_page_offers_a_selector_grouped_by_family(self):
        for path, options in (('/ecuaciones-no-lineales/regla-falsa/', ('Métodos cerrados', 'Métodos abiertos')),
                              ('/sistemas-lineales/gauss-seidel/', ('Métodos directos', 'Métodos iterativos'))):
            response = self.client.get(path)
            self.assertContains(response, 'id="method-select"')
            for label in options:
                self.assertContains(response, f'<optgroup label="{label}">')
        self.assertContains(self.client.get('/ecuaciones-no-lineales/secante/'), 'value="secant" selected')
        self.assertContains(self.client.get('/sistemas-lineales/gauss-seidel/'), 'value="gauss-seidel" selected')

    def test_family_step_is_current_for_every_method_of_the_family(self):
        response = self.client.get('/ecuaciones-no-lineales/secante/')
        topic_nav = response.content.decode().split('class="topic-strip"', 1)[1].split('</nav>', 1)[0]
        self.assertRegex(topic_nav, r'href="/ecuaciones-no-lineales/newton/" aria-current="page"')

    def test_completing_one_method_completes_its_family_step(self):
        self.client.post('/api/nonlinear/progress/', {'topic': 'regla-falsa'}, content_type='application/json')
        self.assertEqual(self.client.get('/').context['route_completed_count'], 1)

    def test_each_method_has_a_worked_example_that_can_be_reproduced(self):
        from linear.catalog import METHODS as LINEAR_METHODS
        from nonlinear.catalog import METHODS
        for slug, prefix in ([(m['slug'], '/ecuaciones-no-lineales/') for m in METHODS.values()]
                             + [(m['slug'], '/sistemas-lineales/') for m in LINEAR_METHODS.values()]):
            response = self.client.get(f'{prefix}{slug}/')
            self.assertContains(response, 'id="ejercicio-resuelto"', msg_prefix=slug)
            self.assertContains(response, f'href="{prefix}{slug}/?', msg_prefix=slug)
        self.assertContains(self.client.get('/ecuaciones-no-lineales/biseccion/'), '1.562500')
        self.assertContains(self.client.get('/sistemas-lineales/gauss-seidel/'), '2.733333')
