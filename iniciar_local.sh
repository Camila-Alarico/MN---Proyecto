#!/usr/bin/env bash
set -euo pipefail
cd -- "$(dirname -- "$0")"
export NUMLEARN_DEBUG=True
export ALLOW_SQLITE=True
export DATABASE_URL=''
export SECRET_KEY='numlearn-local-development-only-do-not-use-in-production'
if [ ! -x .venv/bin/python ]; then
  echo 'Falta el entorno .venv. Créalo con python3 -m venv .venv e instala requirements.txt.'
  exit 1
fi
.venv/bin/python manage.py migrate --noinput
printf '\nAbre http://127.0.0.1:8000 en tu navegador. Para detener: Ctrl+C.\n\n'
exec .venv/bin/python manage.py runserver 127.0.0.1:8000 --noreload
