from django.urls import reverse
from django.utils.functional import SimpleLazyObject

from assessment.scoring import course_score
from nonlinear.practice_bank import TOPICS as PRACTICE_TOPICS
from .views import units_context


def temario(request):
    """Una ubicación y actividades específicas para cada tema, sin índices paralelos."""
    units = units_context(request)
    entries = [entry for unit in units for week in unit['weeks'] for entry in week['entries']]
    total = sum(unit['total'] for unit in units)
    finished = sum(unit['finished'] for unit in units)
    match = request.resolver_match
    slug = match.kwargs.get('slug') if match else None
    if match and match.url_name == 'practice':
        slug = request.GET.get('tema', 'errores')
    entry = next((item for item in entries if item['slug'] == slug), None)
    current = next((unit for unit in units if entry and unit['number'] == entry['unit']), None)
    position = entries.index(entry) if entry else None
    return {
        # Puntaje de las autoevaluaciones (assessment/scoring.py): distinto del avance por temas. Se calcula solo si
        # una plantilla lo imprime y sin crear sesión para quien aún no hizo nada.
        'course_score': SimpleLazyObject(lambda: course_score(request.user, request.session.session_key)),
        'temario_units': units, 'temario_total': total, 'temario_finished': finished,
        'temario_percent': round(finished / total * 100) if total else 0,
        'temario_unit': current, 'course_entry': entry,
        'course_siblings': [item for item in entries if current and item['unit'] == current['number']],
        'course_is_practice': bool(match and match.url_name == 'practice'),
        'course_previous': entries[position - 1] if position is not None and position > 0 else None,
        'course_next': entries[position + 1] if position is not None and position + 1 < len(entries) else None,
        'course_practice_url': f"{reverse('nonlinear:practice')}?tema={slug}" if slug in PRACTICE_TOPICS else None,
        'course_progress_endpoint': (
            '/api/nonlinear/progress/' if entry and entry['kind'] == 'nonlinear' else '/api/linear/progress/'),
        'is_temario': request.path == '/' or request.path.startswith('/temario/'),
    }
