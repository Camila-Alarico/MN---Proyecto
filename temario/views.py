"""Temario del curso: índice por unidades y lecciones nuevas (semanas 1 a 16)."""
from django.http import Http404
from django.shortcuts import render, redirect
from django.urls import reverse

from core.models import UserProgress
from nonlinear.throttle import throttle
from nonlinear.views import json_endpoint

from .catalog import ALL_SLUGS, LESSON_SLUGS, SEQUENCE, TOTAL_WEEKS, UNIT_BY_NUMBER, UNITS
from .lessons import LESSONS
from .navigation import assessment_for

MODULE = 'temario'


def entry_url(entry):
    if entry['kind'] == 'lesson':
        return reverse('temario:lesson', args=[entry['slug']])
    return reverse(f"{entry['kind']}:page", args=[entry['slug']])


def completed_slugs(request):
    """Contenidos completados en cualquier módulo: sesión para invitados, UserProgress con cuenta."""
    if request.user.is_authenticated:
        done = UserProgress.objects.filter(user=request.user, completed=True).values_list('topic', flat=True)
    else:
        done = request.session.get('completed_topics', [])
    return set(done) & ALL_SLUGS


def units_context(request):
    """Unidades con sus semanas, enlaces resueltos y avance. Lo usan el índice, la portada y la barra lateral."""
    done = completed_slugs(request)
    units = []
    for unit in UNITS:
        weeks, total, finished = [], 0, 0
        for week in unit['weeks']:
            entries = [{**entry, 'url': entry_url(entry), 'completed': entry['slug'] in done} for entry in week['entries']]
            total += len(entries)
            finished += sum(entry['completed'] for entry in entries)
            weeks.append({**week, 'entries': entries, 'completed': all(entry['completed'] for entry in entries)})
        units.append({**unit, 'weeks': weeks, 'total': total, 'finished': finished,
                      'percent': round(finished / total * 100) if total else 0, 'assessment': assessment_for(unit['number']),
                      'url': f"{reverse('home')}#unidad-{unit['number']}"})
    return units


def index(request):
    if request.path == reverse('temario:index'):
        return redirect('home')
    units = units_context(request)
    total = sum(unit['total'] for unit in units)
    finished = sum(unit['finished'] for unit in units)
    return render(request, 'temario/index.html', {
        'units': units, 'total_weeks': TOTAL_WEEKS, 'total_items': total, 'finished_items': finished,
        'overall_percent': round(finished / total * 100) if total else 0,
        'next_entry': next((entry for unit in units for week in unit['weeks'] for entry in week['entries']
                            if not entry['completed']), None),
    })


def lesson(request, slug):
    content = LESSONS.get(slug)
    if not content:
        raise Http404()
    position = next(i for i, entry in enumerate(SEQUENCE) if entry['slug'] == slug)
    neighbours = {}
    for key, offset in (('previous', -1), ('next', 1)):
        if 0 <= position + offset < len(SEQUENCE):
            other = SEQUENCE[position + offset]
            neighbours[key] = {**other, 'url': entry_url(other), 'unit_title': UNIT_BY_NUMBER[other['unit']]['title']}
    unit = UNIT_BY_NUMBER[content['unit']]
    siblings = [{**entry, 'url': entry_url(entry)} for week in unit['weeks'] for entry in week['entries']]
    done = completed_slugs(request)
    for sibling in siblings:
        sibling['completed'] = sibling['slug'] in done
    return render(request, 'temario/lesson.html', {
        'lesson': content, 'unit': unit, 'topic': slug, 'siblings': siblings,
        'week_title': next(week['title'] for week in unit['weeks'] if week['week'] == content['week']),
        'completed': slug in done, **neighbours,
    })


@throttle('temario-progress')
@json_endpoint
def progress(request, data):
    """Marca o desmarca una lección como completada. Mismo almacenamiento que los módulos 1 y 2."""
    slug = str(data.get('topic', ''))
    if slug not in LESSON_SLUGS:
        raise Http404()
    completed = bool(data.get('completed', True))
    if request.user.is_authenticated:
        UserProgress.objects.update_or_create(
            user=request.user, module=MODULE, topic=slug,
            defaults={'progress_percentage': 100 if completed else 0, 'completed': completed})
    else:
        topics = set(request.session.get('completed_topics', []))
        topics = topics | {slug} if completed else topics - {slug}
        request.session['completed_topics'] = sorted(topics)
    done = completed_slugs(request)
    unit = UNIT_BY_NUMBER[LESSONS[slug]['unit']]
    entries = [entry['slug'] for week in unit['weeks'] for entry in week['entries']]
    return {'success': True, 'completed': completed,
            'unit_finished': sum(entry in done for entry in entries), 'unit_total': len(entries),
            'message': 'Lección completada. Tu avance quedó guardado.' if completed else 'Lección marcada como pendiente.'}
