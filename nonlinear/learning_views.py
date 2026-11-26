from django.shortcuts import render, redirect

from . import learning
from .practice_bank import catalog
from .services.parser import MathInputError
from .throttle import throttle
from .views import json_endpoint
from assessment.views import page as assessment_page


def theory(request):
    return redirect('/#unidad-3' if request.GET.get('vista') == 'modulo' else '/ecuaciones-no-lineales/errores/')


def practice(request):
    topic = request.GET.get('tema', 'errores')
    focused = topic == 'errores' or topic not in (*learning.TOPICS, 'all')
    exercises = catalog()
    selected = topic if topic in learning.TOPICS else None
    if selected:
        exercises = [item for item in exercises if item['topic'] == selected]
    return render(request, 'nonlinear/practice.html', {
        'practice_topics': {selected: learning.TOPICS[selected]} if selected else learning.TOPICS,
        'selected_topic': selected, 'selected_topic_title': learning.TOPICS.get(selected), 'errors_focus': focused,
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
    # Recupera también prácticas guardadas con la política anterior.
    if state:
        state['locked'] = False
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
        # Salir conserva la actividad y sus respuestas.
        pass
    elif action == 'restart':
        state = learning.restart_practice(state)
    elif action != 'resume':
        raise MathInputError('Acción desconocida.')
    request.session[key] = state
    if not state:
        return {'success': True, 'empty': True}
    return learning.public_practice(state)
