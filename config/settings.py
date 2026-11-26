"""Configuración de NumLearn.

Las variables se leen desde el entorno o desde `.env` en desarrollo. Vercel usa
su entorno de producción, dominios de despliegue y PostgreSQL remoto.
"""
from pathlib import Path

import environ
from django.core.exceptions import ImproperlyConfigured

BASE_DIR = Path(__file__).resolve().parent.parent

env = environ.Env(DEBUG=(bool, False), ALLOW_SQLITE=(bool, False))
IS_VERCEL = env('VERCEL', default='') == '1'
if not IS_VERCEL:
    environ.Env.read_env(BASE_DIR / '.env')

# --- Seguridad básica -------------------------------------------------------

# NUMLEARN_DEBUG prevalece sobre un DEBUG global del sistema.
DEBUG = False if IS_VERCEL else env.bool('NUMLEARN_DEBUG', default=env('DEBUG'))

SECRET_KEY = env('SECRET_KEY', default='')
if not SECRET_KEY or (not DEBUG and (len(SECRET_KEY) < 50 or SECRET_KEY.startswith('replace-'))):
    raise ImproperlyConfigured('Configura SECRET_KEY en .env (al menos 50 caracteres en producción).')

ALLOWED_HOSTS = env.list('ALLOWED_HOSTS', default=['localhost', '127.0.0.1'])
CSRF_TRUSTED_ORIGINS = env.list('CSRF_TRUSTED_ORIGINS', default=[])
if IS_VERCEL:
    # URLs del sistema de Vercel, sin esquema. No se admite cualquier *.vercel.app.
    deployment_hosts = [
        env(name, default='').strip()
        for name in ('VERCEL_URL', 'VERCEL_PROJECT_PRODUCTION_URL', 'VERCEL_BRANCH_URL')
    ]
    deployment_hosts = [host for host in deployment_hosts if host]
    ALLOWED_HOSTS = list(dict.fromkeys([*ALLOWED_HOSTS, *deployment_hosts]))
    CSRF_TRUSTED_ORIGINS = list(dict.fromkeys([
        *CSRF_TRUSTED_ORIGINS, *(f'https://{host}' for host in deployment_hosts),
    ]))

# --- Base de datos ----------------------------------------------------------

database_url = env('DATABASE_URL', default='')
if IS_VERCEL and not database_url:
    database_url = env('POSTGRES_URL', default='')
if database_url:
    DATABASES = {'default': env.db_url_config(database_url)}
    if DATABASES['default']['ENGINE'] != 'django.db.backends.postgresql':
        raise ImproperlyConfigured('DATABASE_URL debe apuntar a PostgreSQL.')
    if IS_VERCEL:
        # Compatible con conexiones agrupadas (Neon/PgBouncer) y funciones efímeras.
        DATABASES['default'].update(
            CONN_MAX_AGE=0, CONN_HEALTH_CHECKS=True, DISABLE_SERVER_SIDE_CURSORS=True,
        )
        options = DATABASES['default'].setdefault('OPTIONS', {})
        options.setdefault('connect_timeout', 10)
        options.setdefault('sslmode', 'require')
elif DEBUG and env('ALLOW_SQLITE'):
    DATABASES = {'default': {'ENGINE': 'django.db.backends.sqlite3', 'NAME': BASE_DIR / 'db.sqlite3'}}
else:
    raise ImproperlyConfigured(
        'Configura PostgreSQL con DATABASE_URL o habilita ALLOW_SQLITE=True y DEBUG=True para desarrollo.'
    )

# --- Aplicaciones -----------------------------------------------------------

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'core',
    'nonlinear',
    'linear',
    'assessment',
    'temario',
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'whitenoise.middleware.WhiteNoiseMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'config.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [BASE_DIR / 'templates'],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
                'core.context_processors.navigation',
                'temario.context_processors.temario',
            ]
        },
    }
]

WSGI_APPLICATION = 'config.wsgi.application'
ASGI_APPLICATION = 'config.asgi.application'

# --- Cuentas ----------------------------------------------------------------

AUTH_PASSWORD_VALIDATORS = [
    {'NAME': 'django.contrib.auth.password_validation.' + name}
    for name in [
        'UserAttributeSimilarityValidator',
        'MinimumLengthValidator',
        'CommonPasswordValidator',
        'NumericPasswordValidator',
    ]
]

LOGIN_REDIRECT_URL = '/'
LOGOUT_REDIRECT_URL = '/'
LOGIN_URL = '/cuenta/login/'

# Recuperación de contraseña. Por defecto los correos se imprimen en la consola del
# servidor (suficiente para desarrollo y demostraciones). En producción define
# EMAIL_URL, por ejemplo: smtp+tls://usuario:clave@smtp.proveedor.com:587
vars().update(env.email_url('EMAIL_URL', default='consolemail://'))
DEFAULT_FROM_EMAIL = env('DEFAULT_FROM_EMAIL', default='NumLearn <no-responder@numlearn.local>')
PASSWORD_RESET_TIMEOUT = 60 * 60 * 24  # 24 horas

# --- Internacionalización ---------------------------------------------------

LANGUAGE_CODE = 'es'
TIME_ZONE = 'America/Lima'
USE_I18N = True
USE_TZ = True

# --- Estáticos --------------------------------------------------------------

STATIC_URL = '/static/'
STATIC_ROOT = BASE_DIR / 'staticfiles'
STATICFILES_DIRS = [BASE_DIR / 'static']
STORAGES = {
    'default': {'BACKEND': 'django.core.files.storage.FileSystemStorage'},
    'staticfiles': {
        'BACKEND': 'django.contrib.staticfiles.storage.StaticFilesStorage'
        if DEBUG
        else 'whitenoise.storage.CompressedManifestStaticFilesStorage'
    },
}

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'
DATA_UPLOAD_MAX_MEMORY_SIZE = 16384

# --- Caché y límite de peticiones a la API ----------------------------------

# LocMem basta con un proceso; con varios workers de Gunicorn cada uno lleva su
# propio contador (el límite efectivo se multiplica por el número de workers).
CACHES = {'default': {'BACKEND': 'django.core.cache.backends.locmem.LocMemCache', 'LOCATION': 'numlearn'}}

# POST por minuto, operación y dirección de conexión. Detrás de un proxy,
# configura también allí el límite por cliente. 0 desactiva el contador local.
NUMLEARN_API_RATE_LIMIT = env.int('NUMLEARN_API_RATE_LIMIT', default=120)

# --- Registro de eventos ----------------------------------------------------

LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {'plain': {'format': '{levelname} {asctime} {name}: {message}', 'style': '{'}},
    'handlers': {'console': {'class': 'logging.StreamHandler', 'formatter': 'plain'}},
    'root': {'handlers': ['console'], 'level': 'WARNING'},
    'loggers': {
        # 400/404 son ruido; los 500 (ERROR) sí interesan en los logs de Render.
        'django.request': {'handlers': ['console'], 'level': 'ERROR', 'propagate': False},
        'nonlinear': {'handlers': ['console'], 'level': 'INFO', 'propagate': False},
        'core': {'handlers': ['console'], 'level': 'INFO', 'propagate': False},
    },
}

# --- Endurecimiento en producción -------------------------------------------

SESSION_COOKIE_HTTPONLY = True
X_FRAME_OPTIONS = 'DENY'

if not DEBUG:
    SECURE_SSL_REDIRECT = env.bool('SECURE_SSL_REDIRECT', default=True)
    SESSION_COOKIE_SECURE = True
    CSRF_COOKIE_SECURE = True
    SECURE_HSTS_SECONDS = 31536000
    SECURE_HSTS_INCLUDE_SUBDOMAINS = True
    SECURE_HSTS_PRELOAD = True
    # Solo detrás de un proxy que elimine X-Forwarded-Proto entrante (Render/Railway).
    SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')
