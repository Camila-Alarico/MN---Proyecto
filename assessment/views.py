from django.core.exceptions import ValidationError
from django.shortcuts import render

from nonlinear.services.parser import MathInputError
from nonlinear.throttle import throttle
from django.utils import timezone
from nonlinear.views import json_endpoint

from . import engine
from .models import Attempt


def _session_key(request):
    if not request.session.session_key:
        request.session.create()
    return request.session.session_key


def _owner_filter(request):
    key = _session_key(request)
    return {'user': request.user} if request.user.is_authenticated else {'session_key': key, 'user__isnull': True}


def _own_attempt(request, data):
    attempt_id = data.get('attempt')
    try:
        attempt = Attempt.objects.get(pk=attempt_id, **_owner_filter(request))
    except (Attempt.DoesNotExist, ValueError, TypeError, ValidationError) as exc:  # id mal formado o ajeno
        raise MathInputError('No se encontró tu evaluación. Vuelve a empezar.') from exc
    return attempt


def page(request, default_scope='curso'):
    """Autoevaluación del curso. `default_scope` permite que cada módulo la abra con su alcance."""
    scope = request.GET.get('alcance')
    scope = scope if scope in engine.SCOPES else default_scope
    _session_key(request)
    return render(request, 'assessment/page.html', {
        'scopes': engine.scope_cards(), 'scope': scope,
        'pass_percent': round(engine.PASS_RATIO * 100),
    })


@throttle('assessment')
@json_endpoint
def api(request, data):
    action = data.get('action')
    away_key = 'assessment_away'

    if action == 'start':
        scope = data.get('scope')
        name = (request.user.get_full_name() or request.user.get_username()
                if request.user.is_authenticated else 'Estudiante')
        request.session.pop(away_key, None)
        attempt = engine.start_attempt(request.user if request.user.is_authenticated else None,
                                       _session_key(request), name, scope)
        return engine.attempt_view(attempt)

    if action == 'resume':
        away = request.session.get(away_key)
        owned = Attempt.objects.filter(finished_at__isnull=True, **_owner_filter(request))
        if away and away.get('attempt'):
            attempt = owned.filter(pk=away['attempt']).first()
        else:
            scope = data.get('scope')
            attempt = owned.filter(**({'scope': scope} if scope in engine.SCOPES else {})).first()
        restarted = False
        resumed_after_short_leave = False
        if attempt and away and away.get('attempt') == str(attempt.pk):
            try:
                away_seconds = timezone.now().timestamp() - float(away['at'])
            except (KeyError, TypeError, ValueError):
                away_seconds = 0
            request.session.pop(away_key, None)
            if away_seconds > 5:
                owner = request.user if request.user.is_authenticated else None
                name = attempt.student_name
                attempt_scope = attempt.scope
                attempt.delete()
                attempt = engine.start_attempt(owner, _session_key(request), name, attempt_scope)
                restarted = True
            else:
                resumed_after_short_leave = True
        elif away:
            request.session.pop(away_key, None)
        if not attempt:
            return {'success': True, 'empty': True}
        state = engine.attempt_view(attempt)
        if restarted:
            state['restarted'] = True
        elif resumed_after_short_leave:
            state['resumed'] = True
        return state

    if action == 'restart':
        attempt = _own_attempt(request, data)
        if attempt.finished:
            raise MathInputError('La evaluación ya terminó; inicia otro intento desde la pantalla inicial.')
        owner = request.user if request.user.is_authenticated else None
        name, scope = attempt.student_name, attempt.scope
        attempt.delete()
        request.session.pop(away_key, None)
        fresh = engine.start_attempt(owner, _session_key(request), name, scope)
        state = engine.attempt_view(fresh)
        state['restarted'] = True
        return state

    if action == 'leave':
        attempt = _own_attempt(request, data)
        if not attempt.finished:
            request.session[away_key] = {'attempt': str(attempt.pk), 'at': timezone.now().timestamp()}
            request.session.modified = True
        return {'success': True}

    if action == 'return':
        attempt = _own_attempt(request, data)
        away = request.session.get(away_key)
        if away and away.get('attempt') == str(attempt.pk):
            request.session.pop(away_key, None)
        return {'success': True}

    attempt = _own_attempt(request, data)
    if action == 'answer':
        return engine.submit(attempt, data)
    if action == 'review':
        return engine.review_attempt(attempt)
    raise MathInputError('Acción desconocida.')


