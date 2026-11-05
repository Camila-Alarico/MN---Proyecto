import json
import logging
from functools import wraps

from django.core.exceptions import RequestDataTooBig
from django.http import Http404, HttpResponsePermanentRedirect, JsonResponse
from django.shortcuts import render
from django.urls import reverse
from django.views.decorators.http import require_POST

from core.models import UserProgress

from .catalog import (DEFAULT_METHOD, FAMILIES, FAMILY_LIST, METHOD_BY_SLUG, METHODS, ROUTE, STUDY_PAGES, TOPIC_SLUGS,
                      WORKED_EXAMPLES)
from .models import CalculationHistory
from .services.comparison import compare_methods
from .services.errors import calculate_errors
from .services.parser import MathInputError
from .services.plotting import sample_function
from .services.solving import run_method
from .throttle import throttle

logger = logging.getLogger(__name__)


def json_endpoint(view):
    @require_POST
    @wraps(view)
    def wrapped(request, *args, **kwargs):
        try:
            if request.content_type != 'application/json':
                raise MathInputError('Envía los datos como application/json.')
            data = json.loads(request.body, parse_constant=lambda value: (_ for _ in ()).throw(ValueError()))
            if not isinstance(data, dict):
                raise MathInputError('El cuerpo debe ser un objeto JSON.')
            return JsonResponse(view(request, data, *args, **kwargs), json_dumps_params={'allow_nan': False})
        except (MathInputError, ValueError, TypeError, KeyError, RequestDataTooBig) as exc:
            message = (
                str(exc) if isinstance(exc, MathInputError)
                else 'Datos inválidos o incompletos. Revisa los campos enviados.'
            )
            return JsonResponse({'success': False, 'error': message}, status=400)
        except Http404:
            return JsonResponse({'success': False, 'error': 'No se encontró el recurso solicitado.'}, status=404)
        except (ArithmeticError, RecursionError, NotImplementedError):
            return JsonResponse(
                {'success': False,
                 'error': 'No se puede evaluar esta expresión de forma segura. Simplifícala o revisa el dominio.'},
                status=400,
            )
        except Exception:
            logger.exception('Error interno en endpoint de NumLearn')
            return JsonResponse(
                {'success': False, 'error': 'No se pudo completar la operación. Inténtalo nuevamente.'}, status=500
            )
    return wrapped


# --- Páginas ----------------------------------------------------------------

def landing(request):
    return render(request, 'nonlinear/landing.html')


def page(request, slug):
    """Destino único de cada contenido: temas de estudio y un simulador por método."""
    if slug in STUDY_PAGES:
        context = {'topic': slug, 'methods': METHODS}
        return render(request, f'nonlinear/{slug}.html', context)

    key = METHOD_BY_SLUG.get(slug)
    if not key:
        raise Http404()
    return render(
        request,
        'nonlinear/simulator.html',
        {'topic': slug, 'method': METHODS[key], 'method_key': key, 'methods': METHODS, 'method_registry': METHODS,
         **method_context('nonlinear:page', key, METHODS, FAMILIES, FAMILY_LIST, ROUTE, WORKED_EXAMPLES)},
    )


def method_context(url_name, key, methods, families, family_list, route, worked_examples):
    """Contexto compartido por los simuladores de ambos módulos: familia, selector y ejercicio resuelto.

    El método se elige dentro del simulador (optgroup por familia) y cada método trae un ejercicio
    resuelto cuyo enlace «Reproducir» apunta a la URL canónica del método con los datos del ejercicio.
    """
    method = methods[key]
    family = {**families[method['family']], 'default_slug': methods[families[method['family']]['default']]['slug']}
    position = next((n for n, step in enumerate(route, start=1) if method['slug'] in step['slugs']), None)
    example = worked_examples[key]
    url = f"{reverse(url_name, args=[method['slug']])}?{example['query']}"
    return {'family': family, 'families': family_list, 'route_position': position,
            'worked_example': {**example, 'url': url}}


def legacy_lab(request):
    """Enlaces heredados `/laboratorio/?method=...`: 301 a la URL canónica del método.

    Antes existían dos URLs para el mismo simulador (`/laboratorio/` y `/biseccion/`). Se conserva
    esta ruta solo para no romper marcadores ni historiales exportados; ningún enlace interno la usa.
    """
    key = request.GET.get('method')
    key = key if key in METHODS else DEFAULT_METHOD
    query = request.GET.copy()
    query.pop('method', None)
    target = reverse('nonlinear:page', args=[METHODS[key]['slug']])
    return HttpResponsePermanentRedirect(f'{target}?{query.urlencode()}' if query else target)


# --- API --------------------------------------------------------------------

@throttle('solve')
@json_endpoint
def solve(request, data, method):
    cleaned, answer = run_method(method, data)
    if request.user.is_authenticated:
        answer['history_id'] = _record_history(request.user, method, cleaned, answer)
    return answer


HISTORY_LIMIT_PER_USER = 300


def _record_history(user, method, cleaned, answer):
    """Guarda el cálculo evitando duplicados consecutivos y acotando el historial."""
    result = {key: value for key, value in answer.items() if key != 'plot'}
    latest = CalculationHistory.objects.filter(user=user).first()  # ordering = -created_at
    if latest and latest.method == method and latest.parameters == cleaned and not latest.favorite:
        latest.result = result
        latest.save(update_fields=['result'])
        return latest.pk
    item = CalculationHistory.objects.create(
        user=user, method=method, function_expression=cleaned['expression'], parameters=cleaned, result=result
    )
    stale = CalculationHistory.objects.filter(user=user, favorite=False).values_list('pk', flat=True)[
        HISTORY_LIMIT_PER_USER:
    ]
    if stale:
        CalculationHistory.objects.filter(pk__in=list(stale)).delete()
    return item.pk


@throttle('graph')
@json_endpoint
def graph(request, data):
    return {'success': True, **sample_function(data['expression'], data['a'], data['b'])}


@throttle('errors')
@json_endpoint
def errors(request, data):
    return calculate_errors(data['true_value'], data['approximate_value'], data.get('tolerance'))


@throttle('compare')
@json_endpoint
def compare(request, data):
    """Recorridos, errores y propagación de varios métodos (sección de comparar.html)."""
    return compare_methods(data)


@json_endpoint
def complete_topic(request, data):
    topic = data.get('topic')
    if topic not in TOPIC_SLUGS:
        raise MathInputError('Tema desconocido.')
    if request.user.is_authenticated:
        UserProgress.objects.update_or_create(
            user=request.user, module='nonlinear', topic=topic,
            defaults={'progress_percentage': 100, 'completed': True},
        )
    else:
        request.session['completed_topics'] = sorted(set(request.session.get('completed_topics', []) + [topic]))
    return {'success': True, 'message': 'Tema completado. Tu progreso está guardado.'}
