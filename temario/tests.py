import json

from django.test import TestCase

from .catalog import LESSON_SLUGS, SEQUENCE, TOTAL_WEEKS, UNITS
from .lessons import LESSONS


class CatalogTests(TestCase):
    def test_sixteen_groups_in_seven_units_without_gaps(self):
        weeks = [week['week'] for unit in UNITS for week in unit['weeks']]
        self.assertEqual(weeks, list(range(1, 17)))
        self.assertEqual((len(UNITS), TOTAL_WEEKS), (7, 16))

    def test_slugs_are_unique_and_every_week_has_content(self):
        slugs = [entry['slug'] for entry in SEQUENCE]
        self.assertEqual(len(slugs), len(set(slugs)))
        for unit in UNITS:
            for week in unit['weeks']:
                self.assertTrue(week['entries'], week['week'])

    def test_lessons_have_every_section(self):
        for slug, lesson in LESSONS.items():
            for key in ('title', 'summary', 'goals', 'idea', 'formulas', 'algorithm', 'example', 'pitfalls', 'lab', 'quiz'):
                self.assertTrue(lesson.get(key), f'{slug}: {key}')
            for row in lesson['example']['rows']:
                self.assertEqual(len(row), len(lesson['example']['columns']), slug)
            for item in lesson['quiz']:
                self.assertIn(item['answer'], range(len(item['options'])), slug)


class PageTests(TestCase):
    def test_index_separates_units_and_links_every_content(self):
        response = self.client.get('/')
        for unit in UNITS:
            self.assertContains(response, f'id="unidad-{unit["number"]}"')
            self.assertContains(response, unit['title'])
        self.assertContains(response, 'href="/temario/runge-kutta/"')
        self.assertContains(response, 'href="/ecuaciones-no-lineales/biseccion/"')
        self.assertContains(response, 'href="/sistemas-lineales/gauss-seidel/"')

    def test_every_lesson_renders_with_its_lab(self):
        for slug, lesson in LESSONS.items():
            response = self.client.get(f'/temario/{slug}/')
            self.assertEqual(response.status_code, 200, slug)
            self.assertContains(response, f'data-lab="{lesson["lab"]["kind"]}"')
            self.assertContains(response, 'data-quick-check')

    def test_unknown_lesson_is_404(self):
        self.assertEqual(self.client.get('/temario/no-existe/').status_code, 404)

    def test_home_sidebar_and_search_reach_the_temario(self):
        home = self.client.get('/')
        self.assertContains(home, 'data-testid="home-temario"')
        self.assertContains(home, 'data-testid="sidebar-temario"')
        self.assertContains(self.client.get('/buscar/?q=simpson'), '/temario/integracion-numerica/')


class ProgressTests(TestCase):
    def post(self, payload):
        return self.client.post('/temario/progreso/', json.dumps(payload), content_type='application/json')

    def test_guest_can_complete_and_undo_a_lesson(self):
        response = self.post({'topic': 'serie-taylor'})
        self.assertEqual(response.json()['unit_finished'], 1)
        self.assertContains(self.client.get('/temario/serie-taylor/'), 'Lección completada')
        self.assertEqual(self.post({'topic': 'serie-taylor', 'completed': False}).json()['unit_finished'], 0)

    def test_unknown_topic_is_rejected(self):
        self.assertEqual(self.post({'topic': 'biseccion'}).status_code, 404)
        self.assertNotIn('biseccion', LESSON_SLUGS)
