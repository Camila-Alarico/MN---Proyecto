"""Pruebas del módulo 2: sistemas de ecuaciones lineales (servicios, API, rutas e integración)."""
import json

from django.contrib.auth.models import User
from django.core.cache import cache
from django.test import TestCase
from django.urls import reverse

from core.models import UserProgress
from nonlinear.models import CalculationHistory

from .catalog import EXAMPLES, TOPIC_SLUGS
from .services.common import residual_inf
from .services.direct import gauss_pivot
from .services.iterative import gauss_seidel

A = [[4, 1, 1], [1, 5, 1], [1, 1, 6]]
B = [9, 14, 21]
BASE = {'size': 3, 'matrix': A, 'vector': B, 'tolerance': 0.000001, 'max_iterations': 100}


class VerificationDataTests(TestCase):
    """Datos de verificación del enunciado."""

    def test_exact_solution_satisfies_the_three_equations(self):
        x = (1, 2, 3)
        for row, b in zip(A, B):
            self.assertEqual(sum(a * v for a, v in zip(row, x)), b)
        self.assertEqual(residual_inf(A, B, x), 0)

    def test_gauss_finds_1_2_3_with_zero_residual(self):
        r = gauss_pivot(A, B)
        self.assertFalse(r['singular'])
        for got, want in zip(r['solution'], (1, 2, 3)):
            self.assertAlmostEqual(got, want, places=12)
        self.assertLess(r['residual'], 1e-12)

    def test_first_gauss_seidel_iteration_from_zero(self):
        r = gauss_seidel(A, B, 0.000001, 100)
        self.assertEqual(r['iterations'][0]['x'], [0.0, 0.0, 0.0])
        first = r['iterations'][1]['x']
        for got, want in zip(first, (2.25, 2.35, 2.7333333333)):
            self.assertAlmostEqual(got, want, places=9)

    def test_gauss_seidel_converges_with_infinity_residual_per_iteration(self):
        r = gauss_seidel(A, B, 0.000001, 100)
        self.assertTrue(r['converged'])
        self.assertLessEqual(r['iterations_count'], 100)
        self.assertLessEqual(r['residual'], 0.000001)
        for got, want in zip(r['solution'], (1, 2, 3)):
            self.assertAlmostEqual(got, want, places=5)
        self.assertTrue(all('residual' in row for row in r['iterations']))
        self.assertTrue(r['dominance']['strict'])

    def test_singular_system_warns_and_shows_no_solution(self):
        r = gauss_pivot([[1, 2], [2, 4]], [3, 6])
        self.assertTrue(r['singular'])
        self.assertIsNone(r['solution'])
        self.assertIn('singular', r['status'].lower())
        self.assertTrue(any('singular' in w for w in r['warnings']))


class PivotingTests(TestCase):
    def test_partial_pivoting_swaps_rows_and_shows_intermediate_matrices(self):
        r = gauss_pivot(*[EXAMPLES['permutado'][k] for k in ('matrix', 'vector')])
        step = r['steps'][0]
        self.assertEqual(step['swap'], {'from': 1, 'to': 2})
        self.assertEqual(step['after_swap'][0][0], 4)
        self.assertEqual(len(r['steps']), 3)
        for got, want in zip(r['solution'], (1, 2, 3)):
            self.assertAlmostEqual(got, want, places=12)

    def test_small_pivot_warning(self):
        r = gauss_pivot([[1, 1], [1, 1 + 1e-9]], [2, 2])
        self.assertFalse(r['singular'])
        self.assertTrue(any('pivote pequeño' in w for w in r['warnings']))

    def test_size_two_system(self):
        r = gauss_pivot([[3, 1], [1, 2]], [9, 8])
        self.assertAlmostEqual(r['solution'][0], 2)
        self.assertAlmostEqual(r['solution'][1], 3)

    def test_zero_matrix_is_singular(self):
        self.assertTrue(gauss_pivot([[0, 0], [0, 0]], [0, 0])['singular'])


class IterativeBehaviourTests(TestCase):
    def test_diverges_when_row_order_breaks_dominance(self):
        e = EXAMPLES['permutado']
        r = gauss_seidel(e['matrix'], e['vector'], 0.000001, 100)
        self.assertFalse(r['converged'])
        self.assertEqual(r['status'], 'Diverge')
        self.assertFalse(r['dominance']['strict'])

    def test_converges_without_strict_dominance(self):
        e = EXAMPLES['sin-dominancia']
        r = gauss_seidel(e['matrix'], e['vector'], 0.000001, 100)
        self.assertTrue(r['converged'])
        self.assertFalse(r['dominance']['strict'])
        self.assertIn('suficiente', r['convergence_note'])

    def test_zero_diagonal_is_reported_without_dividing(self):
        r = gauss_seidel([[0, 1], [1, 0]], [1, 1], 0.000001, 100)
        self.assertEqual(r['status'], 'Diagonal nula')
        self.assertIsNone(r['solution'])

    def test_example_solutions_match_the_solver(self):
        for ex in EXAMPLES.values():
            if ex['solution']:
                r = gauss_pivot(ex['matrix'], ex['vector'])
                for got, want in zip(r['solution'], ex['solution']):
                    self.assertAlmostEqual(got, want, places=9)


class ApiTests(TestCase):
    def setUp(self):
        cache.clear()  # el límite de peticiones usa la caché local

    def post(self, path, payload):
        return self.client.post(path, payload, content_type='application/json')

    def test_gauss_endpoint(self):
        response = self.post('/api/linear/gauss/', BASE)
        self.assertEqual(response.status_code, 200, response.content)
        self.assertAlmostEqual(response.json()['solution'][2], 3)

    def test_seidel_endpoint_requires_tolerance_and_iterations(self):
        response = self.post('/api/linear/seidel/', {'size': 3, 'matrix': A, 'vector': B})
        self.assertEqual(response.status_code, 400)
        self.assertEqual(self.post('/api/linear/seidel/', BASE).json()['status'], 'Convergió')

    def test_singular_system_over_the_api_has_no_unique_solution(self):
        payload = {**BASE, 'size': 2, 'matrix': [[1, 2], [2, 4]], 'vector': [3, 6]}
        for path in ('/api/linear/gauss/', '/api/linear/seidel/', '/api/linear/compare/'):
            response = self.post(path, payload)
            self.assertEqual(response.status_code, 200, path)
            data = response.json()
            part = data['direct'] if path.endswith('compare/') else data
            self.assertIsNone(part['solution'])
            self.assertIn('singular', part['status'].lower())
            if path.endswith('compare/'):
                self.assertIsNone(data['iterative']['solution'])

    def test_compare_reports_both_methods(self):
        data = self.post('/api/linear/compare/', BASE).json()
        self.assertTrue(data['converged'])
        self.assertLess(data['difference_inf'], 1e-5)
        self.assertEqual(data['direct']['method'], 'gauss')

    def test_validation_errors_are_json_400(self):
        bad = [{**BASE, 'size': 4}, {**BASE, 'matrix': [[1, 2], [3, 4]]}, {**BASE, 'vector': [1, 2]},
               {**BASE, 'matrix': [[4, 1, 'x'], [1, 5, 1], [1, 1, 6]]}, {**BASE, 'tolerance': 0},
               {**BASE, 'matrix': [[True, 1, 1], [1, 5, 1], [1, 1, 6]]}, {**BASE, 'max_iterations': 1000}]
        for payload in bad:
            response = self.post('/api/linear/seidel/', payload)
            self.assertEqual(response.status_code, 400, payload)
            self.assertFalse(response.json()['success'])

    def test_requires_post_and_json(self):
        self.assertEqual(self.client.get('/api/linear/gauss/').status_code, 405)
        self.assertEqual(self.client.post('/api/linear/gauss/', {'x': 1}).status_code, 400)
        self.assertEqual(self.post('/api/linear/jacobi/', BASE).status_code, 400)

    def test_fixed_routes_precede_dynamic_method_route(self):
        self.assertEqual(self.post('/api/linear/compare/', BASE).status_code, 200)
        self.assertEqual(self.post('/api/linear/progress/', {'topic': 'formulacion'}).status_code, 200)

    def test_throttle_applies(self):
        with self.settings(NUMLEARN_API_RATE_LIMIT=1):
            self.assertEqual(self.post('/api/linear/gauss/', BASE).status_code, 200)
            self.assertEqual(self.post('/api/linear/gauss/', BASE).status_code, 429)


class HistoryAndProgressTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user('ana', 'ana@example.com', 'x')

    def test_calculations_are_saved_in_calculation_history_and_grouped(self):
        self.client.force_login(self.user)
        for _ in range(2):
            self.client.post('/api/linear/gauss/', BASE, content_type='application/json')
        self.client.post('/api/linear/compare/', BASE, content_type='application/json')
        self.assertEqual(CalculationHistory.objects.filter(user=self.user, method='linear-gauss').count(), 1)
        self.assertEqual(CalculationHistory.objects.filter(user=self.user, method='linear-compare').count(), 1)
        page = self.client.get(reverse('progress'))
        self.assertContains(page, 'Sist. lineales')
        self.assertContains(page, '/sistemas-lineales/eliminacion-gaussiana/?matrix=')

    def test_guest_calculation_is_not_saved(self):
        self.client.post('/api/linear/gauss/', BASE, content_type='application/json')
        self.assertEqual(CalculationHistory.objects.count(), 0)

    def test_progress_for_user_and_guest_adoption_on_login(self):
        self.client.force_login(self.user)
        self.client.post('/api/linear/progress/', {'topic': 'formulacion'}, content_type='application/json')
        self.assertTrue(UserProgress.objects.filter(user=self.user, module='linear', topic='formulacion', completed=True).exists())
        self.client.logout()
        self.client.post('/api/linear/progress/', {'topic': 'gauss-seidel'}, content_type='application/json')
        self.assertEqual(self.client.post('/api/linear/progress/', {'topic': 'newton'}, content_type='application/json').status_code, 400)
        self.client.post(reverse('login'), {'username': 'ana', 'password': 'x'})
        self.assertTrue(UserProgress.objects.filter(user=self.user, module='linear', topic='gauss-seidel').exists())


class RoutingAndPagesTests(TestCase):
    def test_every_topic_has_a_canonical_page(self):
        for slug in TOPIC_SLUGS:
            self.assertEqual(self.client.get(reverse('linear:page', args=[slug])).status_code, 200, slug)
        self.assertEqual(self.client.get('/sistemas-lineales/').status_code, 200)
        self.assertEqual(self.client.get('/sistemas-lineales/inexistente/').status_code, 404)

    def test_legacy_lab_redirects_301_and_precedes_slug_route(self):
        r = self.client.get('/sistemas-lineales/laboratorio/?method=seidel&vector=[1,2]')
        self.assertRedirects(r, '/sistemas-lineales/gauss-seidel/?vector=%5B1%2C2%5D', status_code=301, fetch_redirect_response=False)
        r = self.client.get('/sistemas-lineales/laboratorio/')
        self.assertRedirects(r, '/sistemas-lineales/eliminacion-gaussiana/', status_code=301, fetch_redirect_response=False)

    def test_section_is_part_of_the_same_navigation(self):
        home = self.client.get('/')
        self.assertContains(home, 'href="/sistemas-lineales/eliminacion-gaussiana/"')
        self.assertContains(home, 'href="/sistemas-lineales/"')
        found = self.client.get(reverse('search'), {'q': 'Gauss-Seidel'})
        self.assertContains(found, '/sistemas-lineales/gauss-seidel/')

    def test_interface_explains_unknowns_size_and_convergence(self):
        lab = self.client.get('/sistemas-lineales/comparacion-metodos/')
        self.assertContains(lab, 'índice normalizado de demanda')
        self.assertContains(lab, 'id="size"')
        theory = self.client.get('/sistemas-lineales/formulacion/')
        self.assertContains(theory, 'suficiente')
        self.assertContains(theory, 'no necesaria')
        self.assertContains(theory, '10^{-12}')
