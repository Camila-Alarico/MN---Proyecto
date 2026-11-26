"""Configuración de producción aislada del .env y de la conexión de pruebas."""
import json
import os
from pathlib import Path
import subprocess
import sys

from django.test import SimpleTestCase


ROOT = Path(__file__).resolve().parent.parent
ENV_KEYS = (
    'SECRET_KEY', 'DEBUG', 'NUMLEARN_DEBUG', 'ALLOW_SQLITE', 'DATABASE_URL',
    'POSTGRES_URL', 'VERCEL', 'VERCEL_URL', 'VERCEL_PROJECT_PRODUCTION_URL',
    'VERCEL_BRANCH_URL', 'ALLOWED_HOSTS', 'CSRF_TRUSTED_ORIGINS',
)
READ_SETTINGS = """
import json, runpy
from django.http.request import validate_host
s = runpy.run_path('config/settings.py')
print(json.dumps({
    'debug': s['DEBUG'], 'hosts': s['ALLOWED_HOSTS'],
    'origins': s['CSRF_TRUSTED_ORIGINS'], 'database': s['DATABASES']['default'],
    'foreign_host_allowed': validate_host('unrelated.vercel.app', s['ALLOWED_HOSTS']),
    'secure_cookies': s.get('SESSION_COOKIE_SECURE', False),
}))
"""


class VercelConfigurationTests(SimpleTestCase):
    def load_settings(self, **changes):
        env = {key: value for key, value in os.environ.items() if key not in ENV_KEYS}
        env.update(
            VERCEL='1', SECRET_KEY='isolated-production-test-key-with-more-than-fifty-characters-123456789',
            DATABASE_URL='postgres://test:example@db.example.test/numlearn',
        )
        env.update(changes)
        return subprocess.run(
            [sys.executable, '-c', READ_SETTINGS], cwd=ROOT, env=env,
            capture_output=True, text=True, timeout=15,
        )

    def test_generated_and_custom_hosts_accept_post_requests_without_wildcard(self):
        result = self.load_settings(
            VERCEL_URL='numlearn-deployment.vercel.app',
            VERCEL_PROJECT_PRODUCTION_URL='numlearn.example.org',
            VERCEL_BRANCH_URL='numlearn-main.vercel.app',
            ALLOWED_HOSTS='extra.example.org',
            CSRF_TRUSTED_ORIGINS='https://extra.example.org',
        )
        self.assertEqual(result.returncode, 0, result.stderr)
        config = json.loads(result.stdout)
        self.assertCountEqual(config['hosts'], [
            'extra.example.org', 'numlearn-deployment.vercel.app',
            'numlearn.example.org', 'numlearn-main.vercel.app',
        ])
        self.assertCountEqual(config['origins'], [f'https://{host}' for host in config['hosts']])
        self.assertFalse(config['foreign_host_allowed'])

    def test_vercel_never_exposes_debug_even_with_development_variables(self):
        result = self.load_settings(DEBUG='release', NUMLEARN_DEBUG='True', ALLOW_SQLITE='True')
        self.assertEqual(result.returncode, 0, result.stderr)
        config = json.loads(result.stdout)
        self.assertFalse(config['debug'])
        self.assertTrue(config['secure_cookies'])

    def test_neon_postgres_url_is_supported_with_pooler_compatible_options(self):
        result = self.load_settings(
            DATABASE_URL='', POSTGRES_URL='postgres://test:example@pooler.example.test/numlearn',
        )
        self.assertEqual(result.returncode, 0, result.stderr)
        database = json.loads(result.stdout)['database']
        self.assertEqual(database['ENGINE'], 'django.db.backends.postgresql')
        self.assertEqual(database['HOST'], 'pooler.example.test')
        self.assertEqual(database['CONN_MAX_AGE'], 0)
        self.assertTrue(database['DISABLE_SERVER_SIDE_CURSORS'])
        self.assertEqual(database['OPTIONS']['sslmode'], 'require')
        self.assertEqual(database['OPTIONS']['connect_timeout'], 10)

    def test_database_url_and_explicit_tls_options_take_precedence(self):
        result = self.load_settings(
            DATABASE_URL='postgres://test:example@primary.example.test/db?sslmode=verify-full&connect_timeout=5',
            POSTGRES_URL='postgres://test:example@other.example.test/db',
        )
        self.assertEqual(result.returncode, 0, result.stderr)
        database = json.loads(result.stdout)['database']
        self.assertEqual(database['HOST'], 'primary.example.test')
        self.assertEqual(database['OPTIONS']['sslmode'], 'verify-full')
        self.assertEqual(int(database['OPTIONS']['connect_timeout']), 5)

    def test_missing_secret_fails_instead_of_generating_inconsistent_session_keys(self):
        result = self.load_settings(SECRET_KEY='')
        self.assertNotEqual(result.returncode, 0)
        self.assertIn('Configura SECRET_KEY', result.stderr)

    def test_missing_database_never_uses_ephemeral_sqlite_on_vercel(self):
        result = self.load_settings(DATABASE_URL='', POSTGRES_URL='', ALLOW_SQLITE='True', DEBUG='True')
        self.assertNotEqual(result.returncode, 0)
        self.assertIn('Configura PostgreSQL', result.stderr)
