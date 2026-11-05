"""Motor de evaluación: composición del intento, corrección en el servidor e indicadores de integridad.

Principios (el objetivo es demostrar comprensión, no solo obtener una respuesta):
  * Las respuestas correctas nunca viajan al navegador antes de contestar.
  * Los problemas paso a paso usan datos distintos en cada intento (semilla guardada en el servidor).
  * No se puede avanzar sin completar el paso (o la pregunta) anterior; el servidor lo impone.
  * Las respuestas abiertas se puntúan con una rúbrica de conceptos y se valoran con una rúbrica de conceptos.
  * Se registran salidas de la pestaña, pegados, copias y recargas como INDICADORES, no como prueba.
"""
import math
import random
import re
import secrets
import unicodedata

from django.utils import timezone

from nonlinear.services.parser import MathInputError

from . import generators
from .bank import BANK, MODULE_1, MODULE_2, MULTI, OPEN, SOURCES, STEPS, SUBTOPICS, instantiate_steps
from .models import Answer, Attempt

PASS_RATIO = 0.70
MAX_STEP_TRIES = 3
STEP_POINTS = {1: 1.0, 2: 0.5, 3: 0.25}
MAX_TEXT = 2000

# (selección múltiple, respuesta abierta, problemas paso a paso): teoría primero, práctica al final.
SCOPES = {
    'errores': {'title': 'Solo errores numéricos · Tema del módulo 1', 'topics': ('errores',), 'mix': (4, 3, 3),
                'description': 'Evaluación específica de medidas de error, origen del error y tolerancia.'},
    'modulo-1': {'title': 'Módulo 1 · Ecuaciones no lineales y errores', 'topics': MODULE_1, 'mix': (5, 3, 3),
                 'description': 'Evalúa el módulo completo: errores, separación de raíces, bisección, falsa posición, Newton-Raphson, secante y raíces múltiples.'},
    'modulo-2': {'title': 'Módulo 2 · Sistemas lineales', 'topics': MODULE_2, 'mix': (4, 3, 3),
                 'description': 'Evalúa el módulo completo: formulación, métodos directos, pivoteo, Jacobi, Gauss-Seidel y convergencia.'},
    'curso': {'title': 'Todo el curso (módulos 1 y 2)', 'topics': MODULE_1 + MODULE_2, 'mix': (5, 3, 3),
              'description': 'Preguntas de ambos módulos.'},
}
PHASES = {'multi': 'Conceptos', 'open': 'Explicación', 'steps': 'Problema paso a paso'}


def bank_size(scope=None):
    topics = set(SCOPES[scope]['topics']) if scope else None
    return sum(1 for q in BANK.values() if topics is None or q['topic'] in topics)


def scope_cards():
    return [
        {'key': key, 'title': info['title'], 'description': info['description']}
        for key, info in SCOPES.items()
    ]


# --- Composición ----------------------------------------------------------------------------------

def _pick(pool, count, rng, avoid=frozenset()):
    """Toma `count` preguntas repartiéndolas entre subtemas/temas y prefiriendo las que el estudiante no vio hace poco."""
    groups = {}
    for q in pool:
        groups.setdefault(q.get('sub') or q['topic'], []).append(q)
    names = list(groups)
    rng.shuffle(names)
    for items in groups.values():
        rng.shuffle(items)
        items.sort(key=lambda q: q['id'] in avoid, reverse=True)  # pop() toma del final: primero las no vistas
    chosen, turn = [], 0
    while len(chosen) < count:
        live = [name for name in names if groups[name]]
        if not live:
            break
        # Primero los grupos con preguntas no vistas; solo se repite una vista cuando ya no queda nada nuevo.
        fresh = [name for name in live if groups[name][-1]['id'] not in avoid]
        options = fresh or live
        chosen.append(groups[options[turn % len(options)]].pop())
        turn += 1
    return chosen


def compose(scope, rng=None, avoid=frozenset()):
    """Arma un intento nuevo: mezcla de formatos, preguntas distintas a las recientes y opciones barajadas."""
    rng = rng or random.SystemRandom()
    info = SCOPES[scope]
    topics = set(info['topics'])
    plan = []
    for pool, count in zip((MULTI, OPEN, STEPS), info['mix']):
        for q in _pick([q for q in pool if q['topic'] in topics], count, rng, avoid):
            entry = {'id': q['id'], 'seed': rng.getrandbits(32)}
            if q['type'] == 'multi':
                order = list(range(len(q['options'])))
                rng.shuffle(order)
                entry['order'] = order
            plan.append(entry)
    # Los formatos se intercalan en un orden nuevo en cada intento; no quedan
    # primero todas las preguntas de selección, luego las abiertas, etc.
    rng.shuffle(plan)
    return plan


def recent_question_ids(user, session_key, limit=2):
    """Preguntas de los últimos intentos del mismo estudiante: el siguiente intento intenta no repetirlas."""
    attempts = (Attempt.objects.filter(user=user) if user else Attempt.objects.filter(session_key=session_key, user__isnull=True))
    seen = set()
    for plan in attempts.order_by('-started_at').values_list('plan', flat=True)[:limit]:
        seen.update(entry['id'] for entry in plan)
    return seen


def start_attempt(owner_user, session_key, student_name, scope):
    if scope not in SCOPES:
        raise MathInputError('Elige una evaluación disponible.')
    plan = compose(scope, avoid=recent_question_ids(owner_user, session_key))
    return Attempt.objects.create(user=owner_user, session_key=session_key, student_name=student_name, scope=scope,
                                  plan=plan, total=len(plan))


# --- Vista pública de una pregunta (sin respuestas) ---------------------------------------------------

def _source(topic):
    title, url, template = SOURCES[topic]
    return {'title': title, 'url': url}


def _case(entry, question):
    return question['case'](random.Random(f'{question["id"]}:{entry["seed"]}')) if question.get('case') else None


def _shown(step):
    if step['kind'] == 'choice':
        return next(label for value, label in step['options'] if value == step['answer'])
    return generators.n(step['answer'])


def _steps_view(attempt, index, entry, question):
    data = instantiate_steps(question, entry['seed'])
    state = attempt.state.get(str(index), {'step': 0, 'tries': 0, 'points': [], 'revealed': []})
    items = []
    for k, step in enumerate(data['steps']):
        if k < state['step']:
            items.append({'status': 'done', 'label': f'Paso {k + 1}', 'prompt': step['prompt'], 'shown': _shown(step),
                          'points': state['points'][k], 'revealed': k in state['revealed']})
        elif k == state['step']:
            item = {'status': 'current', 'label': f'Paso {k + 1}', 'prompt': step['prompt'], 'kind': step['kind'],
                    'tries_left': MAX_STEP_TRIES - state['tries']}
            if step['kind'] == 'choice':
                item['options'] = step['options']
            items.append(item)
        else:
            items.append({'status': 'locked', 'label': f'Paso {k + 1}'})
    return {'intro': question['prompt'], 'given': data['given'], 'items': items, 'current': state['step'],
            'count': len(items), 'done': state['step'] >= len(items)}


def question_view(attempt, index):
    entry = attempt.plan[index]
    q = BANK[entry['id']]
    view = {'index': index, 'type': q['type'], 'topic': q['topic'],
            'phase': PHASES[q['type']], 'source': _source(q['topic']), 'prompt': q['prompt']}
    if q['type'] == 'multi':
        view['options'] = [q['options'][i] for i in entry['order']]
        view['hint'] = 'Marca todas las opciones que correspondan. Puede haber más de una correcta.'
    elif q['type'] == 'open':
        case = _case(entry, q)
        if case:
            view['prompt'] = case['prompt']
        view.update(min_words=q['min_words'], max_chars=MAX_TEXT,
                    hint=f'Escribe con tus palabras (mínimo {q["min_words"]} palabras). Se valoran el procedimiento y la justificación.')
    else:
        view['steps'] = _steps_view(attempt, index, entry, q)
    return view


def attempt_view(attempt):
    """Estado público del intento: la pregunta actual o el resumen final."""
    if attempt.current >= len(attempt.plan):
        return finish_attempt(attempt)
    return {'success': True, 'attempt': str(attempt.id), 'scope': attempt.scope, 'scope_title': SCOPES[attempt.scope]['title'],
            'done': False, 'question': question_view(attempt, attempt.current)}


# --- Corrección --------------------------------------------------------------------------------------

def normalize(text):
    text = unicodedata.normalize('NFD', text.lower())
    return ''.join(c for c in text if unicodedata.category(c) != 'Mn')


def parse_number(value):
    if isinstance(value, bool) or not isinstance(value, (int, float, str)):
        raise MathInputError('Escribe un número. Usa punto decimal.')
    text = str(value).strip().replace(',', '.').replace('%', '').replace(' ', '').replace('−', '-')
    try:
        number = float(text)
    except ValueError:
        raise MathInputError('Escribe un número válido (por ejemplo 0.25 o -1.5).') from None
    if not math.isfinite(number) or abs(number) > 1e9:
        raise MathInputError('Escribe un número finito dentro de un rango razonable.')
    return number


def _numbers_in(text):
    return [float(m.replace(',', '.')) for m in re.findall(r'-?\d+(?:[.,]\d+)?', text)]


def _near(got, want, floor=5e-5):
    return abs(got - want) <= max(floor, 1e-3 * abs(want))


FUNCTION_WORDS = frozenset('de la el que es se en un una y por con para los las del al lo como si no su sus le o a e mas pero porque cuando'.split())


def looks_like_prose(text):
    """Una explicación real tiene ~30 % de palabras de enlace; una lista de palabras clave casi ninguna."""
    tokens = [t for t in re.findall(r'[^\W\d_]+', normalize(text))]  # solo palabras: los números no cuentan
    return bool(tokens) and sum(t in FUNCTION_WORDS for t in tokens) / len(tokens) >= 0.15


def score_open(question, text, case):
    words = len(re.findall(r'\w+', text))
    if words >= question['min_words'] and not looks_like_prose(text):
        return {'score': 0.0, 'words': words, 'hits': [], 'missed': [label for label, _ in question['rubric']],
                'short': False, 'list_like': True, 'number_ok': None}
    if words < question['min_words']:
        return {'score': 0.0, 'words': words, 'hits': [], 'missed': [label for label, _ in question['rubric']],
                'short': True, 'number_ok': None}
    norm = normalize(text)
    hits, missed = [], []
    for label, patterns in question['rubric']:
        (hits if any(re.search(p, norm) for p in patterns) else missed).append(label)
    total, got = len(question['rubric']), len(hits)
    number_ok = None
    if case and case.get('must'):
        nums = _numbers_in(text)
        number_ok = all(any(_near(n_, want) for n_ in nums) for want in case['must'])
        total, got = total + 1, got + (1 if number_ok else 0)
    return {'score': got / total, 'words': words, 'hits': hits, 'missed': missed, 'short': False, 'number_ok': number_ok}


def _advance(attempt):
    attempt.current += 1
    attempt.save(update_fields=['current', 'state'])


def _record(attempt, index, q, response, score):
    return Answer.objects.create(attempt=attempt, index=index, question_id=q['id'], kind=q['type'], topic=q['topic'],
                                 response=response, score=score)


def _submit_multi(attempt, index, entry, q, data):
    selected = data.get('selected')
    if (not isinstance(selected, list) or not selected or len(selected) > len(q['options'])
            or any(isinstance(i, bool) or not isinstance(i, int) or not 0 <= i < len(q['options']) for i in selected)
            or len(set(selected)) != len(selected)):
        raise MathInputError('Selecciona al menos una opción antes de comprobar.')
    chosen = {entry['order'][i] for i in selected}
    right, wrong = len(chosen & q['correct']), len(chosen - q['correct'])
    score = max(0.0, (right - wrong) / len(q['correct']))
    _record(attempt, index, q, {'selected': sorted(chosen), 'texts': [q['options'][i] for i in sorted(chosen)]}, score)
    _advance(attempt)
    detail = [{'text': q['options'][o], 'chosen': o in chosen, 'correct': o in q['correct']} for o in entry['order']]
    label = 'Correcto.' if score == 1 else 'Parcialmente correcto.' if score > 0 else 'Incorrecto.'
    return {'type': 'multi', 'score': score, 'correct': score == 1, 'feedback': f'{label} {q["explanation"]}', 'options': detail,
            'question_done': True}


def _submit_open(attempt, index, entry, q, data):
    text = data.get('text')
    if not isinstance(text, str) or not text.strip():
        raise MathInputError('Escribe tu respuesta antes de comprobar.')
    text = text.strip()
    if len(text) > MAX_TEXT:
        raise MathInputError(f'La respuesta admite hasta {MAX_TEXT} caracteres.')
    result = score_open(q, text, _case(entry, q))
    _record(attempt, index, q, {'text': text, 'hits': result['hits'], 'missed': result['missed'], 'words': result['words'],
                                'number_ok': result['number_ok']}, result['score'])
    _advance(attempt)
    if result.get('list_like'):
        feedback = 'Parece una lista de palabras sueltas. Explica con oraciones completas cómo y por qué; esta pregunta puntúa 0.'
    elif result['short']:
        feedback = f'Tu respuesta tiene {result["words"]} palabras; se pedían al menos {q["min_words"]}. Esta pregunta puntúa 0.'
    elif result['score'] >= 0.99:
        feedback = 'Respuesta completa: incluiste todos los elementos que se valoraban.'
    elif result['score'] > 0:
        feedback = 'Respuesta parcial: faltaron algunos elementos. Compara con la respuesta modelo.'
    else:
        feedback = 'No se detectaron los elementos esperados. Compara con la respuesta modelo.'
    return {'type': 'open', 'score': result['score'], 'correct': result['score'] >= 0.99, 'feedback': feedback,
            'hits': result['hits'], 'missed': result['missed'], 'number_ok': result['number_ok'], 'model': q['model'],
            'review_note': 'La puntuación automática es orientativa: revisa los elementos detectados y compárala con la respuesta modelo.', 'question_done': True}


def _submit_steps(attempt, index, entry, q, data):
    steps = instantiate_steps(q, entry['seed'])['steps']
    state = attempt.state.setdefault(str(index), {'step': 0, 'tries': 0, 'points': [], 'revealed': [], 'tries_log': [], 'last': []})
    k = state['step']
    if k >= len(steps):
        raise MathInputError('Este problema ya está completo.')
    if data.get('step') != k:
        raise MathInputError('Ese paso no es el actual. Completa los pasos en orden.')
    step = steps[k]
    raw = data.get('value')
    if step['kind'] == 'number':
        given = parse_number(raw)
        ok = abs(given - step['answer']) <= max(step.get('tol', 5e-5), 1e-3 * abs(step['answer']))
    else:
        if not isinstance(raw, str) or raw not in {v for v, _ in step['options']}:
            raise MathInputError('Elige una de las respuestas.')
        given, ok = raw, raw == step['answer']
    state['tries'] += 1
    typed = generators.n(given) if step['kind'] == 'number' else next(label for value, label in step['options'] if value == raw)
    state.setdefault('last', []).append(typed)
    revealed = False
    if ok:
        state['points'].append(STEP_POINTS[state['tries']])
    elif state['tries'] >= MAX_STEP_TRIES:
        state['points'].append(0.0)
        state['revealed'].append(k)
        revealed = True
    if ok or revealed:
        state.setdefault('tries_log', []).append(state['tries'])
        state.setdefault('given', []).append(list(state['last']))
        state['step'] = k + 1
        state['tries'] = 0
        state['last'] = []
    result = {'type': 'steps', 'correct': ok, 'step_done': ok or revealed, 'revealed': revealed,
              'feedback': ('Correcto.' if ok else f'Todavía no. Este paso era: {_shown(step)}. {step["explain"]}' if revealed
                           else f'No coincide. Revisa tu cálculo. Te quedan {MAX_STEP_TRIES - state["tries"]} intento(s) en este paso.'),
              'question_done': False}
    if ok:
        result['explain'] = step['explain']
    if state['step'] >= len(steps):
        points = state['points']
        score = sum(points) / len(points)
        _record(attempt, index, q, {'steps': [{'prompt': s['prompt'], 'shown': _shown(s), 'points': points[i],
                                               'revealed': i in state['revealed'], 'given': state['given'][i]} for i, s in enumerate(steps)],
                                    'tries': state.get('tries_log', [])}, score)
        _advance(attempt)
        result.update(question_done=True, score=score)
    else:
        attempt.save(update_fields=['state'])
    return result


def submit(attempt, data):
    if attempt.finished:
        raise MathInputError('Esta evaluación ya terminó.')
    index = data.get('index')
    if isinstance(index, bool) or not isinstance(index, int) or index != attempt.current:
        raise MathInputError('La pregunta ya cambió. Recarga para recuperar tu evaluación.')
    entry = attempt.plan[index]
    q = BANK[entry['id']]
    handler = {'multi': _submit_multi, 'open': _submit_open, 'steps': _submit_steps}[q['type']]
    result = handler(attempt, index, entry, q, data)
    # Misma pregunta (paso intermedio) o la siguiente: el navegador decide cuándo mostrarla.
    shown_index = index
    return {'success': True, 'result': result, 'question': question_view(attempt, shown_index),
            'next': attempt_view(attempt) if result['question_done'] else None}


# --- Cierre y resumen ---------------------------------------------------------------------------------

def recompute(attempt):
    scores = [a.effective_score for a in attempt.answers.all()]
    attempt.points = round(sum(scores), 4)
    attempt.passed = attempt.points / max(attempt.total, 1) >= PASS_RATIO
    attempt.save(update_fields=['points', 'passed'])


def wrong_answers(attempt):
    return [a for a in attempt.answers.all() if a.effective_score < 0.99]


def finish_attempt(attempt):
    if not attempt.finished:
        attempt.finished_at = timezone.now()
        attempt.save(update_fields=['finished_at'])
        recompute(attempt)
    return {'success': True, 'attempt': str(attempt.id), 'scope': attempt.scope, 'scope_title': SCOPES[attempt.scope]['title'], 'done': True,
            'points': attempt.points, 'percent': round(100 * attempt.points / max(attempt.total, 1)),
            'passed': attempt.passed, 'pass_percent': round(PASS_RATIO * 100), 'wrong': len(wrong_answers(attempt))}


def review_attempt(attempt):
    """Solo las preguntas que el estudiante respondió mal (o a medias), con su respuesta y la correcta."""
    if not attempt.finished:
        raise MathInputError('Termina la evaluación para revisar tus errores.')
    items = []
    for a in wrong_answers(attempt):
        q, entry = BANK[a.question_id], attempt.plan[a.index]
        item = {'index': a.index + 1, 'type': a.kind, 'phase': PHASES[a.kind], 'topic': SOURCES[a.topic][0], 'url': SOURCES[a.topic][1],
                'subtopic': SUBTOPICS.get(q.get('sub')), 'score': round(a.effective_score, 2), 'prompt': q['prompt']}
        if a.kind == 'multi':
            chosen = set(a.response.get('selected', []))
            item.update(options=[{'text': q['options'][o], 'chosen': o in chosen, 'correct': o in q['correct']} for o in entry['order']],
                        explanation=q['explanation'])
        elif a.kind == 'open':
            case = _case(entry, q)
            item.update(prompt=case['prompt'] if case else q['prompt'], answer=a.response.get('text', ''), missed=a.response.get('missed', []),
                        model=q['model'])
        else:
            data = instantiate_steps(q, entry['seed'])
            saved = a.response.get('steps', [])
            item.update(given=data['given'], steps=[
                {'prompt': step['prompt'], 'typed': saved[i].get('given', []) if i < len(saved) else [], 'correct': _shown(step),
                 'points': saved[i]['points'] if i < len(saved) else 0, 'revealed': saved[i]['revealed'] if i < len(saved) else False,
                 'explain': step['explain']} for i, step in enumerate(data['steps'])])
        items.append(item)
    return {'success': True, 'review': items, 'wrong': len(items)}
