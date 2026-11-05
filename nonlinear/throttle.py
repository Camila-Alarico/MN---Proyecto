"""Límite simple de peticiones por IP para la API, basado en la caché de Django.

No requiere dependencias nuevas. El límite se configura con NUMLEARN_API_RATE_LIMIT
(peticiones por minuto; 0 lo desactiva). Con varios workers de Gunicorn y LocMemCache
cada proceso cuenta por separado; para un límite exacto usa una caché compartida (Redis).
"""
import time
from functools import wraps

from django.conf import settings
from django.core.cache import cache
from django.http import JsonResponse


def client_ip(request):
    # Forwarded headers can be supplied by the caller. Only the transport peer
    # is trusted here; per-client proxy limits belong at the configured edge.
    return request.META.get('REMOTE_ADDR', 'desconocido')


def throttle(scope):
    def decorator(view):
        @wraps(view)
        def wrapped(request, *args, **kwargs):
            limit = getattr(settings, 'NUMLEARN_API_RATE_LIMIT', 0)
            if limit and request.method == 'POST':
                key = f'throttle:{scope}:{client_ip(request)}:{int(time.time() // 60)}'
                cache.add(key, 0, timeout=120)
                try:
                    count = cache.incr(key)
                except ValueError:  # la clave expiró entre add e incr
                    count = 1
                if count > limit:
                    return JsonResponse(
                        {
                            'success': False,
                            'error': 'Demasiadas solicitudes en poco tiempo. Espera un minuto y vuelve a intentarlo.',
                        },
                        status=429,
                    )
            return view(request, *args, **kwargs)

        return wrapped

    return decorator
