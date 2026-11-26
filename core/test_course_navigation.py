from collections import deque
from html.parser import HTMLParser
from urllib.parse import urljoin, urlsplit

from django.contrib.auth import get_user_model
from django.test import TestCase

from assessment.engine import compose
from assessment.bank import BANK
from temario.catalog import SEQUENCE
from temario.views import entry_url


class PageLinks(HTMLParser):
    def __init__(self, html):
        super().__init__()
        self.hrefs, self.ids = [], set()
        self.feed(html)

    def handle_starttag(self, tag, attrs):
        attrs = dict(attrs)
        if 'id' in attrs:
            self.ids.add(attrs['id'])
        if tag == 'a' and attrs.get('href'):
            self.hrefs.append(attrs['href'])


class CourseNavigationTests(TestCase):
    def test_internal_course_links_and_section_bookmarks_are_reachable(self):
        queue = deque(['/', '/avance/', '/empieza-aqui/', '/recursos/', '/evaluacion/'])
        seen, anchors, failures = {}, [], []
        while queue and len(seen) < 250:
            target = queue.popleft()
            if target in seen:
                continue
            response = self.client.get(target, follow=True)
            seen[target] = response
            if response.status_code != 200:
                failures.append((target, response.status_code))
                continue
            if 'text/html' not in response.get('Content-Type', ''):
                continue
            for href in PageLinks(response.content.decode()).hrefs:
                url = urlsplit(urljoin('http://testserver' + response.request['PATH_INFO'], href))
                if url.netloc != 'testserver' or url.path.startswith(('/static/', '/cuenta/', '/admin/')):
                    continue
                destination = url.path + ('?' + url.query if url.query else '')
                if url.fragment:
                    anchors.append((target, destination, url.fragment))
                if destination not in seen:
                    queue.append(destination)
        self.assertFalse(queue, 'El recorrido superó el límite de páginas de la auditoría.')
        for source, destination, fragment in anchors:
            response = seen[destination]
            if response.status_code == 200 and fragment not in PageLinks(response.content.decode()).ids:
                failures.append((source, destination + '#' + fragment))
        self.assertEqual(failures, [])
        self.assertGreaterEqual(len(seen), len(SEQUENCE))

    def test_error_lesson_retains_all_legacy_explorer_controls_and_animations(self):
        response = self.client.get('/ecuaciones-no-lineales/errores/')
        for element in ('fundamento', 'tipos', 'aplicacion', 'practicar', 'errors-form',
                        'error-example', 'true-value', 'approximate-value', 'error-tolerance',
                        'approximation-slider', 'try-boundary', 'display-decimals', 'error-plot',
                        'tolerance-feedback', 'tolerance-interval', 'challenge-feedback',
                        'absolute', 'relative', 'percentage', 'error-worked'):
            with self.subTest(element=element):
                self.assertContains(response, f'id="{element}"')
        for scene in ('errors', 'derivative-perturbation'):
            self.assertContains(response, f'data-scene="{scene}"', count=1)
        self.assertContains(response, 'data-panel="check"')

    def test_old_indexes_redirect_to_the_single_course(self):
        for path, target in [('/temario/', '/'), ('/teoria/', '/'),
                             ('/ecuaciones-no-lineales/', '/#unidad-3'),
                             ('/ecuaciones-no-lineales/teoria/?vista=modulo', '/#unidad-3'),
                             ('/sistemas-lineales/', '/#unidad-4')]:
            with self.subTest(path=path):
                self.assertRedirects(self.client.get(path), target, fetch_redirect_response=False)

    def test_all_topics_are_reachable_with_their_course_location(self):
        home = self.client.get('/')
        for entry in SEQUENCE:
            with self.subTest(topic=entry['slug']):
                url = entry_url(entry)
                self.assertContains(home, f'href="{url}"')
                page = self.client.get(url)
                self.assertEqual(page.status_code, 200)
                self.assertEqual(page.context['course_entry']['slug'], entry['slug'])
                self.assertContains(page, f'href="/#unidad-{entry["unit"]}"')

    def test_practice_is_filtered_on_the_server_to_the_selected_topic(self):
        for topic in ('errores', 'biseccion', 'regla-falsa', 'newton', 'secante', 'punto-fijo', 'raices-multiples'):
            response = self.client.get('/ecuaciones-no-lineales/practica/', {'tema': topic})
            self.assertTrue(response.context['exercises'])
            self.assertEqual({item['topic'] for item in response.context['exercises']}, {topic})
            self.assertEqual(response.context['course_entry']['slug'], topic)

    def test_root_scope_is_not_mixed_with_errors(self):
        for _ in range(10):
            plan = compose('unidad-2')
            self.assertTrue(plan)
            self.assertNotIn('errores', {BANK[item['id']]['topic'] for item in plan})

    def test_guest_progress_includes_old_and_new_lessons(self):
        self.client.post('/api/nonlinear/progress/', {'topic': 'biseccion'}, content_type='application/json')
        self.client.post('/temario/progreso/', {'topic': 'serie-taylor'}, content_type='application/json')
        response = self.client.get('/avance/')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context['temario_finished'], 2)

    def test_guest_new_lesson_progress_survives_sign_in(self):
        user = get_user_model().objects.create_user('learner', password='test-only-password')
        self.client.post('/temario/progreso/', {'topic': 'serie-taylor'}, content_type='application/json')
        self.client.force_login(user)
        self.assertEqual(self.client.get('/avance/').context['temario_finished'], 1)
