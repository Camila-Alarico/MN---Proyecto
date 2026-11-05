from django.shortcuts import render, redirect

from . import learning
from .practice_bank import catalog
from .services.parser import MathInputError
from .throttle import throttle
from .views import json_endpoint
from assessment.views import page as assessment_page


def theory(request):
    if request.GET.get('vista') == 'modulo':
        return render(request, 'nonlinear/theory.html')
    return redirect('nonlinear:page', slug='errores')


def practice(request):
    topic = request.GET.get('tema', 'errores')
    focused = topic == 'errores' or topic not in (*learning.TOPICS, 'all')
    exercises = catalog()
    return render(request, 'nonlinear/practice.html', {
        'practice_topics': learning.TOPICS, 'errors_focus': focused,
        'exercises': [item for item in exercises if item['topic'] == 'errores'] if focused else exercises,
    })


def assessment(request):
    """La autoevaluación del módulo 1 vive en `assessment`; el selector permite elegir módulo 1, módulo 2 o el curso completo."""
    return assessment_page(request, default_scope='modulo-1')


@throttle('learning')
@json_endpoint
def activity(request, data, mode):
    if mode != 'practice':
        raise MathInputError('Actividad desconocida.')
    scope = data.get('scope', 'modulo')
    if scope not in ('errores', 'modulo'):
        raise MathInputError('Recorrido desconocido.')
    key = 'learning_practice' + ('_errores' if scope == 'errores' else '')
    state = request.session.get(key)
    action = data.get('action', 'resume')
    if action == 'start':
        if scope == 'errores' and data.get('topic') != 'errores':
            raise MathInputError('Este recorrido trabaja únicamente errores numéricos.')
        state = learning.start_practice(data.get('topic'), state, data.get('exercise'))
    elif action == 'check':
        if not state:
            raise MathInputError('Inicia una actividad antes de responder.')
        result = learning.check_practice(state, data)
        request.session[key] = state
        return result
    elif action == 'leave':
        # El navegador avisa de que el estudiante salió de la página (visibilitychange, blur o pagehide).
        if data.get('id') and state and data.get('id') != state['id']:
            return {'success': True, 'ignored': True}  # aviso de una práctica anterior ya reemplazada
        learning.lock_practice(state)
    elif action == 'restart':
        state = learning.restart_practice(state)
    elif action != 'resume':
        raise MathInputError('Acción desconocida.')
    request.session[key] = state
    if not state:
        return {'success': True, 'empty': True}
    return learning.public_practice(state)
