"""Pruebas del menú lateral auto-ocultable y de las animaciones de los ejemplos de teoría."""
import re

from django.conf import settings
from django.contrib.staticfiles import finders
from django.test import TestCase
from django.urls import reverse

from linear.catalog import METHODS as LINEAR_METHODS
from nonlinear.catalog import METHODS as NONLINEAR_METHODS

SCENE_FILES = ['js/animations/root-scenes.js', 'js/animations/error-scenes.js', 'js/animations/linear-scenes.js']


def scenes_in(html):
    return re.findall(r'data-scene="([a-z-]+)"', html)


class SidebarDockTests(TestCase):
    def test_sidebar_has_pin_button_and_left_edge_hotzone(self):
        html = self.client.get('/').content.decode()
        self.assertIn('id="sidebar-pin"', html)
        self.assertIn('aria-pressed="false"', html)
        self.assertIn('aria-label="Fijar menú lateral"', html)
        self.assertIn('class="dart-flight"', html)  # icono de dardo
        self.assertIn('id="sidebar-hotzone"', html)
        self.assertIn("localStorage.getItem('numlearn:sidebar-pinned')", html)
        self.assertIn('css/sidebar-dock.css', html)

    def test_pinned_preference_is_applied_before_stylesheets(self):
        html = self.client.get('/').content.decode()
        self.assertLess(html.index('numlearn:sidebar-pinned'), html.index('css/app.css'))


class TheoryAnimationTests(TestCase):
    def test_every_worked_example_offers_an_animation(self):
        for key, method in NONLINEAR_METHODS.items():
            with self.subTest(method=key):
                html = self.client.get(reverse('nonlinear:page', args=[method['slug']])).content.decode()
                self.assertEqual(scenes_in(html), [key])
                self.assertIn(f'data-testid="anim-start-{key}"', html)
                self.assertIn('Iniciar animación', html)
        for key, method in LINEAR_METHODS.items():
            with self.subTest(method=key):
                html = self.client.get(reverse('linear:page', args=[method['slug']])).content.decode()
                self.assertEqual(scenes_in(html), [key])

    def test_theory_topics_with_examples_offer_animations(self):
        expected = {
            reverse('nonlinear:page', args=['errores']): ['errors', 'derivative-perturbation'],
            reverse('nonlinear:page', args=['conceptos']): ['roots-case'],
            reverse('nonlinear:page', args=['polinomios']): ['multiple-roots'],
            reverse('linear:page', args=['formulacion']): ['gauss', 'seidel'],
        }
        for url, scenes in expected.items():
            with self.subTest(url=url):
                response = self.client.get(url)
                self.assertEqual(response.status_code, 200)
                self.assertEqual(scenes_in(response.content.decode()), scenes)

    def test_launcher_is_hidden_until_javascript_builds_the_stage(self):
        html = self.client.get(reverse('nonlinear:page', args=['biseccion'])).content.decode()
        self.assertRegex(html, r'class="anim-launch" data-anim-launch hidden')
        self.assertRegex(html, r'class="anim-stage" data-anim-stage hidden')

    def test_each_template_scene_is_registered_in_javascript(self):
        source = ''
        for path in SCENE_FILES:
            found = finders.find(path)
            self.assertIsNotNone(found, path)
            with open(found, encoding='utf-8') as handle:
                source += handle.read()
        pages = [reverse('nonlinear:page', args=[m['slug']]) for m in NONLINEAR_METHODS.values()]
        pages += [reverse('linear:page', args=[m['slug']]) for m in LINEAR_METHODS.values()]
        pages += [reverse('nonlinear:page', args=[slug]) for slug in ('errores', 'conceptos', 'polinomios')]
        pages += [reverse('linear:page', args=['formulacion'])]
        used = {scene for url in pages for scene in scenes_in(self.client.get(url).content.decode())}
        self.assertTrue(used)
        for scene in used:
            with self.subTest(scene=scene):
                self.assertRegex(source, rf"[\s{{,]'?{re.escape(scene)}'?: ")

    def test_animation_assets_are_served(self):
        for path in ['js/theory-animation.js', 'js/animations/engine.js', 'js/animations/plot.js',
                     'js/animations/scenes.js', 'js/animations/format.js', 'css/theory-animation.css', 'css/sidebar-dock.css']:
            with self.subTest(path=path):
                self.assertIsNotNone(finders.find(path))
        self.assertIn('static', settings.STATIC_URL)
