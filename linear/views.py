import logging

from django.http import Http404, HttpResponsePermanentRedirect
from django.shortcuts import render
from django.urls import reverse

from core.models import UserProgress
from nonlinear.models import CalculationHistory
from nonlinear.services.parser import MathInputError
from nonlinear.throttle import throttle
from nonlinear.views import HISTORY_LIMIT_PER_USER, json_endpoint, method_context

from .catalog import (DEFAULT_METHOD, EXAMPLES, FAMILIES, FAMILY_LIST, HISTORY_PREFIX, METHOD_BY_SLUG, METHODS, ROUTE,
                      STUDY_PAGES, TOPIC_SLUGS, WORKED_EXAMPLES)
from .services.solving import run_comparison, run_system

logger = logging.getLogger(__name__)


# --- Páginas ----------------------------------------------------------------

def landing(request):
    return render(request, 'linear/landing.html')


def page(request, slug):
    """Destino único de cada contenido: temas de estudio y una página por método."""
    context = {'topic': slug, 'methods': METHODS, 'examples': EXAMPLES}
    if slug in STUDY_PAGES:
        return render(request, f'linear/{slug}.html', context)
    key = METHOD_BY_SLUG.get(slug)
    if not key:
        raise Http404()
    return render(request, 'linear/simulator.html', {
        **context, 'method': METHODS[key], 'method_key': key,
        **method_context('linear:page', key, METHODS, FAMILIES, FAMILY_LIST, ROUTE, WORKED_EXAMPLES)})


def legacy_lab(request):
    """Enlaces `/laboratorio/?method=...`: 301 a la URL canónica del método (conserva el resto de parámetros)."""
    key = request.GET.get('method')
    key = key if key in METHODS else DEFAULT_METHOD
    query = request.GET.copy()
    query.pop('method', None)
    target = reverse('linear:page', args=[METHODS[key]['slug']])
    return HttpResponsePermanentRedirect(f'{target}?{query.urlencode()}' if query else target)


# --- API --------------------------------------------------------------------

def _record_history(user, method, cleaned, answer):
    """Guarda el cálculo en CalculationHistory (agrupa duplicados consecutivos y acota el historial)."""
    key = HISTORY_PREFIX + method
    label = '; '.join(' '.join(f'{v:.8g}' for v in row) + f' | {b:.8g}'
                      for row, b in zip(cleaned['matrix'], cleaned['vector']))[:200]
    summary = {k: answer.get(k) for k in ('status', 'converged', 'iterations_count')}
    summary['solution'] = (answer.get('solution') if method != 'compare'
                           else (answer['direct'].get('solution')))
    summary['residual'] = answer.get('residual') if method != 'compare' else answer['direct'].get('residual')
    params = {k: cleaned[k] for k in ('size', 'matrix', 'vector', 'tolerance', 'max_iterations')}
    latest = CalculationHistory.objects.filter(user=user).first()
    if latest and latest.method == key and latest.parameters == params and not latest.favorite:
        latest.result = summary
        latest.save(update_fields=['result'])
        return latest.pk
    item = CalculationHistory.objects.create(user=user, method=key, function_expression=label,
                                             parameters=params, result=summary)
    stale = CalculationHistory.objects.filter(user=user, favorite=False).values_list('pk', flat=True)[
        HISTORY_LIMIT_PER_USER:]
    if stale:
        CalculationHistory.objects.filter(pk__in=list(stale)).delete()
    return item.pk


@throttle('linear-solve')
@json_endpoint
def solve(request, data, method):
    cleaned, answer = run_system(method, data)
    if request.user.is_authenticated:
        answer['history_id'] = _record_history(request.user, method, cleaned, answer)
    return answer


@throttle('linear-compare')
@json_endpoint
def compare(request, data):
    cleaned, answer = run_comparison(data)
    if request.user.is_authenticated:
        answer['history_id'] = _record_history(request.user, 'compare', cleaned, answer)
    return answer


@json_endpoint
def complete_topic(request, data):
    topic = data.get('topic')
    if topic not in TOPIC_SLUGS:
        raise MathInputError('Tema desconocido.')
    if request.user.is_authenticated:
        UserProgress.objects.update_or_create(
            user=request.user, module='linear', topic=topic,
            defaults={'progress_percentage': 100, 'completed': True},
        )
    else:  # misma lista de sesión que el módulo 1 (los slugs son únicos en todo el curso)
        request.session['completed_topics'] = sorted(set(request.session.get('completed_topics', []) + [topic]))
    return {'success': True, 'message': 'Tema completado. Tu progreso está guardado.'}
