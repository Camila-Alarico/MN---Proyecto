"""Comprueba producción y aplica migraciones antes de publicar en Vercel.

Vercel instala requirements.txt y ejecuta collectstatic automáticamente.
"""
import os
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')

import django
from django.core.management import call_command
from django.core.exceptions import ImproperlyConfigured
from django.db import connection, transaction


def main():
    django.setup()
    if connection.vendor != 'postgresql':
        raise ImproperlyConfigured('El despliegue necesita una base PostgreSQL remota.')
    call_command('check', deploy=True, fail_level='WARNING')
    # Evita que dos despliegues concurrentes intenten crear la misma tabla.
    lock_id = 617063140
    # El bloqueo es de transacción: funciona también con poolers en ese modo y
    # se libera al terminar o fallar, sin dejar bloqueos de sesión en PgBouncer.
    with transaction.atomic():
        with connection.cursor() as cursor:
            cursor.execute("SET LOCAL lock_timeout = '60s'")
            cursor.execute('SELECT pg_advisory_xact_lock(%s)', [lock_id])
        call_command('migrate', interactive=False)


if __name__ == '__main__':
    main()
