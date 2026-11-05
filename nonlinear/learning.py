"""Práctica guiada y banco teórico. Las respuestas se comprueban en el servidor."""
import math
import random
import secrets
from decimal import Decimal
from urllib.parse import urlencode

from .services.parser import MathInputError, parse_function
from .practice_bank import TOPICS, METHOD_KEYS, METHOD_TASKS, SOURCES, cases, exercise_case, first_iteration, curve


STEP_TITLES = ['Comprender', 'Elegir', 'Preparar', 'Calcular', 'Comprobar']


def numeric(data, key):
    value = data.get(key)
    if isinstance(value, bool) or not isinstance(value, (int, float, str)):
        raise MathInputError('Completa los campos numéricos. Usa punto decimal.')
    try:
        number = float(value)
    except (ValueError, OverflowError):
        raise MathInputError('Introduce un número válido; puedes usar notación científica.') from None
    if not math.isfinite(number) or abs(number) > 1e6:
        raise MathInputError('Introduce un número finito dentro del rango del ejercicio.')
    return number


def close(got, expected):
    return math.isclose(got, expected, abs_tol=5e-6, rel_tol=1e-6)


def start_practice(topic, previous=None, exercise=None):
    if not isinstance(topic, str) or topic not in TOPICS:
        raise MathInputError('Elige una de las prácticas disponibles.')
    count = len(cases(topic))
    if exercise is not None:
        if not isinstance(exercise, str) or exercise not in [f'{topic}-{i}' for i in range(count)]:
            raise MathInputError('El ejercicio no pertenece al tema elegido.')
        variant = int(exercise.rsplit('-', 1)[1])
    else:
        variant = ((previous['variant'] + 1 + secrets.randbelow(count-1)) % count
                   if previous and previous.get('topic') == topic else secrets.randbelow(count))
    return {'id': secrets.token_hex(12), 'topic': topic, 'variant': variant, 'step': 0, 'values': {}, 'mistakes': 0,
            'locked': False, 'locks': 0, 'attempt': 1}


def lock_practice(state):
    """Bloquea la práctica en curso porque el estudiante salió de la página.

    El bloqueo vive en la sesión del servidor: recargar o volver más tarde no recupera el avance.
    Una práctica ya terminada no se bloquea (no hay nada que proteger).
    """
    if state and not state.get('locked') and state['step'] < 5:
        state['locked'] = True
        state['locks'] = state.get('locks', 0) + 1
    return state


def restart_practice(state):
    """Repite desde el inicio el mismo ejercicio: pasos, datos y errores vuelven a cero."""
    if not state:
        raise MathInputError('No hay una práctica que repetir. Elige un ejercicio.')
    fresh = start_practice(state['topic'], exercise=f"{state['topic']}-{state['variant']}")
    fresh['attempt'] = state.get('attempt', 1) + 1
    fresh['locks'] = state.get('locks', 0)
    return fresh


def shuffled(options, state, label):
    """Mezcla las opciones una vez por intento: estable al recargar, distinta al repetir o cambiar de ejercicio."""
    ordered = [list(item) for item in options]
    random.Random(f"{state['id']}:{state.get('attempt', 1)}:{label}").shuffle(ordered)
    return ordered


def case(state):
    return exercise_case(state)


def absolute_error(data):
    # Los enunciados decimales son datos exactos del ejercicio, incluso en el límite.
    return float(abs(Decimal(str(data['v'])) - Decimal(str(data['approx']))))


def field(key, label, hint=''):
    return {'key': key, 'label': label, 'hint': hint}


def tex_number(value):
    text = f'{value:.12g}'
    if 'e' in text:
        coefficient, exponent = text.split('e')
        return rf'{coefficient}\times 10^{{{int(exponent)}}}'
    return text


def formula(tex, fallback):
    return {'tex': tex, 'fallback': fallback}


def error_context(state):
    data = case(state)
    context = {'given': [
        {'label': 'Referencia', **formula(rf'v={tex_number(data["v"])}', f'v = {data["v"]:g}')},
        {'label': 'Aproximación', **formula(rf'\widetilde v={tex_number(data["approx"])}', f'ṽ = {data["approx"]:g}')},
        {'label': 'Tolerancia absoluta', **formula(rf'\tau={tex_number(data["tolerance"])}', f'τ = {data["tolerance"]:g}')},
    ]}
    if state['step'] >= 4:
        context['known'] = formula(rf'E_a={tex_number(state["values"]["x"])}', f'Ea = {state["values"]["x"]:g}')
    if state['step'] == 3:
        context['reference_formula'] = formula(r'E_a=\left|v-\widetilde v\right|', 'Ea = |referencia − aproximación|')
    return context


def check_errors(state, payload):
    """Una comprobación por campo; no revelar el resultado final antes de acertar."""
    data, values, step = case(state), state['values'], state['step']
    checks = []

    def add(key, valid, message, tex=None, fallback=''):
        item = {'field': key, 'correct': valid, 'message': message}
        if tex:
            item['formula'] = formula(tex, fallback)
        checks.append(item)

    if step == 2:
        v, approx = numeric(payload, 'v'), numeric(payload, 'approx')
        add('v', close(v, data['v']), 'La referencia está identificada.' if close(v, data['v']) else 'Usa el valor de referencia del enunciado, conservando su signo.')
        add('approx', close(approx, data['approx']), 'La aproximación está identificada.' if close(approx, data['approx']) else 'Usa el valor medido o aproximado; no lo intercambies con la referencia.')
    elif step == 3:
        x = numeric(payload, 'x')
        expected = absolute_error(data)
        message = 'El error absoluto está bien calculado.' if close(x, expected) else 'El error absoluto es una distancia y no puede ser negativo.' if x < 0 else 'Resta referencia y aproximación; después toma el valor absoluto.'
        add('x', close(x, expected), message,
            rf'E_a=\left|{tex_number(data["v"])}-({tex_number(data["approx"])})\right|',
            f'Ea = |{data["v"]:g} − ({data["approx"]:g})|')
        if close(x, expected):
            values['x'] = expected
    elif step == 4:
        ea, v, tolerance = values['x'], data['v'], data['tolerance']
        if v == 0:
            for key in ('relative', 'percentage'):
                valid = payload.get(key) == 'undefined'
                add(key, valid, 'Correcto: no está definido porque la referencia es cero.' if valid else
                    'No se puede dividir entre cero. No definido no significa cero.', r'v=0\quad\Longrightarrow\quad E_r,E_p\;\text{no definidos}', 'v = 0: Er y Ep no definidos')
            accepted = ea <= tolerance
            valid = payload.get('decision') == ('yes' if accepted else 'no')
            add('decision', valid, 'La comparación absoluta es correcta.' if valid else 'Aunque el relativo no esté definido, puedes comparar Ea con la tolerancia absoluta.', r'E_a\le\tau', 'Ea ≤ τ')
            return checks
        relative, percentage = numeric(payload, 'relative'), numeric(payload, 'percentage')
        expected = ea / abs(v)
        relative_ok, percentage_ok = close(relative, expected), close(percentage, 100*expected)
        if relative_ok:
            message = 'El error relativo está bien. Es una proporción sin unidades.'
        elif relative < 0:
            message = 'En esta actividad usamos el error relativo absoluto: no lleva signo negativo.'
        elif close(relative, ea):
            message = 'Has repetido el error absoluto. Falta dividirlo entre el valor absoluto de la referencia.'
        elif close(relative, 100*expected):
            message = 'Ese número corresponde al porcentaje. El relativo se escribe antes de multiplicar por 100.'
        else:
            message = 'Divide el error absoluto entre |v|. El denominador es la referencia, no la tolerancia ni la aproximación.'
        add('relative', relative_ok, message,
            rf'E_r=\frac{{E_a}}{{|v|}}=\frac{{{tex_number(ea)}}}{{|{tex_number(v)}|}}',
            f'Er = Ea / |v| = {tex_number(ea)} / |{v:g}|')
        if percentage_ok:
            message = 'El porcentaje está bien. Se interpreta por cada cien unidades de referencia.'
        elif close(percentage, expected):
            message = 'Has escrito la proporción relativa. Falta multiplicarla por 100 para expresarla en porcentaje.'
        elif not relative_ok and close(percentage, 100*relative):
            message = 'Multiplicaste tu relativo por 100, pero ese valor de partida necesita corrección. Revisa primero el campo anterior.'
        else:
            message = 'El porcentaje se obtiene multiplicando el relativo correcto por 100. Escribe solo el número en este campo.'
        add('percentage', percentage_ok, message, r'E_p=100\,E_r\;\%', 'Ep = 100 × Er %')
        accepted = ea <= tolerance
        decision_ok = payload.get('decision') == ('yes' if accepted else 'no')
        equality = ea == tolerance
        message = ('La comparación con la tolerancia es correcta.' if decision_ok else
                   'La igualdad también cuenta: estar justo en el límite sí cumple.' if equality and accepted else
                   'Compara el error absoluto con la tolerancia absoluta. No uses el relativo ni el porcentaje.')
        relation = r'\le' if accepted else '>'
        add('decision', decision_ok, message,
            rf'E_a\le\tau\;?\qquad {tex_number(ea)}\;{relation}\;{tex_number(tolerance)}',
            f'Ea ≤ τ: {tex_number(ea)} {"≤" if accepted else ">"} {tolerance:g}')
    return checks


def public_practice(state):
    topic, step, data = state['topic'], state['step'], case(state)
    if state.get('locked'):
        return {'success': True, 'locked': True, 'id': state['id'], 'topic': topic, 'title': TOPICS[topic],
                'exercise': f"{topic}-{state['variant']}", 'exercise_title': data['title'], 'locks': state.get('locks', 1),
                'message': 'Saliste de la página durante la práctica. Para que el resultado refleje tu trabajo individual, '
                           'la práctica se bloqueó y no se puede retomar donde la dejaste: debes repetirla desde el inicio.'}
    answer = {'success': True, 'id': state['id'], 'topic': topic, 'title': TOPICS[topic],
              'exercise': f"{topic}-{state['variant']}", 'exercise_title': data['title'],
              'step': step, 'steps': STEP_TITLES, 'mistakes': state['mistakes'], 'done': step == 5,
              'source': dict(zip(('title', 'url'), SOURCES[topic]))}
    if topic == 'errores':
        answer['problem'] = data['context']
        answer['math_context'] = error_context(state)
        answer['reference_zero'] = data['v'] == 0
        answer['context_note'] = data['context']
    else:
        f = parse_function(data['expression'])
        answer['expression'] = data['expression']
        answer['problem'] = data['context']
        answer['problem_formula'] = formula(('g(x)=' if topic == 'punto-fijo' else 'f(x)=') + f.latex,
                                             ('g(x) = ' if topic == 'punto-fijo' else 'f(x) = ') + data['expression'])
        if topic == 'punto-fijo':
            original = parse_function(data['reference'])
            answer['problem_formula'] = formula(r'f(x)='+original.latex+r'=0,\qquad g(x)='+f.latex, 'f(x) = '+data['reference']+' = 0; g(x) = '+data['expression'])
        if step in (1, 2):
            answer['curve'] = curve(state)
            answer['diagonal'] = topic == 'punto-fijo'
            answer['graph_caption'] = ('Busca la intersección de g(x) con la diagonal y = x.' if topic == 'punto-fijo' else
                                       'La raíz doble toca el eje sin cambiar de signo. Observa los valores cercanos al contacto.' if topic == 'raices-multiples' else
                                       'Localiza el cruce con el eje horizontal y consulta los valores antes de elegir datos.')
    if step == 5:
        params = {key: value for key, value in state['values'].items() if key in ('a', 'b', 'x0', 'x1')}
        if topic == 'errores':
            answer['next_url'] = '/ecuaciones-no-lineales/autoevaluacion/'
            answer['next_label'] = 'Comprobar conceptos →'
            ea, v = state['values']['x'], data['v']
            answer['results'] = [
                {'label': 'Error absoluto', **formula(rf'E_a={tex_number(ea)}', f'Ea = {tex_number(ea)}')},
                {'label': 'Error relativo', **(formula(r'E_r\;\text{no definido}', 'Er no definido') if v == 0 else formula(rf'E_r={tex_number(ea/abs(v))}', f'Er = {tex_number(ea/abs(v))}'))},
                {'label': 'Error porcentual', **(formula(r'E_p\;\text{no definido}', 'Ep no definido') if v == 0 else formula(rf'E_p={tex_number(100*ea/abs(v))}\,\%', f'Ep = {tex_number(100*ea/abs(v))} %'))},
            ]
            answer['verdict'] = 'Cumple la tolerancia' if ea <= data['tolerance'] else 'No cumple la tolerancia'
        else:
            params.update(expression=data['expression'], tolerance=.000001)
            answer['next_url'] = f"/ecuaciones-no-lineales/{topic}/?{urlencode(params)}#simulator"
        return answer
    if step == 0:
        answer.update(prompt='¿Qué tipo de problema estás resolviendo?', choices=shuffled([['error', 'Evaluar una aproximación'], ['root', 'Encontrar una raíz'], ['linear', 'Resolver un sistema lineal']], state, 'paso-0'))
    elif step == 1:
        if topic == 'errores':
            answer.update(prompt='¿Qué medida conserva las unidades de la referencia?', choices=shuffled([['absolute', 'Error absoluto'], ['relative', 'Error relativo'], ['percentage', 'Error porcentual']], state, 'paso-1'))
        else:
            answer.update(prompt=METHOD_TASKS[topic][0] + ' ¿Qué método realiza ese procedimiento?',
                          choices=shuffled([[key, TOPICS[slug]] for slug, key in METHOD_KEYS.items()], state, 'paso-1'))
    elif step == 2:
        if topic == 'errores':
            answer.update(prompt='Identifica los datos del enunciado.', fields=[field('v', 'Valor de referencia'), field('approx', 'Valor aproximado')])
        elif topic in ('biseccion', 'regla-falsa'):
            answer.update(prompt='Mira la gráfica y elige un intervalo con cambio de signo.', fields=[field('a', 'Extremo a', 'Entre 0 y 4'), field('b', 'Extremo b', 'Mayor que a, hasta 4')], hint='Estas funciones son continuas. Busca un extremo por debajo del eje y otro por encima. Si un extremo ya es raíz, elige otro para practicar el paso.')
        else:
            low, high = (data['low'], data['high']) if topic == 'punto-fijo' else (.25, 4)
            fields = [field('x0', 'Punto inicial x₀', f'Entre {low:g} y {high:g}')]
            if topic == 'secante':
                fields.append(field('x1', 'Segundo punto x₁', 'Distinto de x₀; entre 0.25 y 4'))
            answer.update(prompt='Observa la gráfica y prepara los puntos iniciales.', fields=fields,
                          hint={'secante': 'Elige dos puntos distintos, con imágenes distintas. No es obligatorio que encierren la raíz.',
                                'newton': 'Busca un inicio cercano al cruce. Evita puntos donde la derivada sea cero; la gráfica orienta, pero no garantiza convergencia.',
                                'raices-multiples': 'La raíz doble toca el eje sin cambio de signo. Elige un punto cercano, distinto de la raíz, donde f′² − f f″ permita el paso.',
                                'punto-fijo': 'Elige un punto del intervalo indicado. Estas transformaciones llevan ese intervalo a sí mismo y allí son contracciones.'}[topic])
    elif step == 3:
        if topic == 'errores':
            answer.update(prompt='¿Qué distancia hay entre ambos valores?', fields=[{**field('x', 'Error absoluto'), 'formula': formula(r'E_a=|v-\widetilde v|', 'Ea = |v − ṽ|'), 'note': 'Conserva las unidades de la referencia.'}], hint='Resta los dos valores y toma la magnitud de la diferencia.')
        else:
            values = ', '.join(f'{key} = {value:g}' for key, value in state['values'].items())
            answer.update(prompt=f'Con {values}, calcula la primera aproximación nueva.', fields=[field('x', 'Nueva aproximación x₂' if topic == 'secante' else 'Primera aproximación m' if topic == 'biseccion' else 'Nueva aproximación x₁')],
                          calculation_formula=formula(*METHOD_TASKS[topic][1:]), hint='Evalúa las funciones en tus datos iniciales; conserva los signos y redondea solo al final.')
            f = parse_function(data['expression'])
            if topic in ('newton', 'raices-multiples'):
                answer['derivative_formula'] = formula(r"f\prime(x)="+f.derivative().latex, 'f′(x) = '+str(f.derivative().expression))
            if topic == 'raices-multiples':
                answer['second_derivative_formula'] = formula(r"f\prime\prime(x)="+f.derivative(2).latex, 'f″(x) = '+str(f.derivative(2).expression))
    elif topic == 'errores':
        answer.update(prompt='Compara la precisión con el límite permitido.', fields=[
            {**field('relative', 'Error relativo'), 'formula': formula(r'E_r=\frac{E_a}{|v|}', 'Er = Ea / |v|'), 'note': 'Proporción sin unidades. No multipliques todavía por 100.'},
            {**field('percentage', 'Error porcentual (%)'), 'formula': formula(r'E_p=100\,E_r\;\%', 'Ep = 100 × Er %'), 'note': 'Escribe solo el número, sin el símbolo %.'},
            {**field('decision', '¿El error absoluto cumple la tolerancia?'), 'formula': formula(r'E_a\le\tau', 'Ea ≤ τ'), 'note': 'La igualdad también cumple.', 'options': [['yes', 'Sí, cumple'], ['no', 'No cumple']]}
        ], hint='Convierte la distancia en proporción, después en porcentaje y compara Ea con τ.')
    else:
        x = state['values']['x']
        if topic == 'regla-falsa':
            fields = [field('new_a', 'Nuevo extremo a'), field('new_b', 'Nuevo extremo b'), field('residual', 'Residuo |f(x nuevo)|')]
            hint = 'Evalúa el signo en el punto nuevo. Conserva el subintervalo con cambio de signo; si el residuo es cero, ambos extremos coinciden en la raíz.'
        else:
            fields = [field('bound', 'Cota de error del punto medio' if topic == 'biseccion' else 'Paso |x nuevo − x anterior|'), field('residual', 'Residuo |g(x nuevo) − x nuevo|' if topic == 'punto-fijo' else 'Residuo |f(x nuevo)|')]
            hint = ('Cota = (b − a)/2. No es lo mismo que el residuo.' if topic == 'biseccion' else
                    'El paso compara la nueva aproximación con la anterior (x₁ en secante). No es una cota general del error verdadero. Evalúa el residuo por separado.')
        answer.update(prompt=f'Con la aproximación {x:.12g}, comprueba tu trabajo.', fields=fields, hint=hint)
    if topic == 'errores' and step == 4 and data['v'] == 0:
        answer['prompt'] = '¿Qué medidas siguen teniendo sentido si la referencia es cero?'
        answer['hint'] = 'El error absoluto es una distancia válida. El relativo divide entre |v| y aquí ese denominador es cero.'
        for item in answer['fields'][:2]:
            item['options'] = shuffled([['zero', 'Es cero'], ['undefined', 'No está definido'], ['absolute', 'Es igual al absoluto']], state, 'cero-' + item['key'])
            item['note'] = 'Distingue una medida no definida de una medida cuyo valor es cero.'
    return answer


def check_practice(state, payload):
    if state.get('locked'):
        raise MathInputError('Esta práctica está bloqueada porque saliste de la página. Repítela desde el inicio.')
    if payload.get('id') != state['id'] or type(payload.get('step')) is not int or payload.get('step') != state['step'] or state['step'] == 5:
        raise MathInputError('Este paso ya cambió. Recarga la práctica para continuar donde te quedaste.')
    topic, step, data, values = state['topic'], state['step'], case(state), state['values']
    correct, feedback, checks = False, '', []
    if topic == 'errores' and step >= 2:
        checks = check_errors(state, payload)
        correct = all(item['correct'] for item in checks)
        wrong = sum(not item['correct'] for item in checks)
        feedback = f'Revisa {wrong} {"campo" if wrong == 1 else "campos"}. Las indicaciones están junto a tu respuesta.'
    elif step in (0, 1):
        wanted = ('error' if topic == 'errores' else 'root') if step == 0 else ('absolute' if topic == 'errores' else METHOD_KEYS[topic])
        correct = payload.get('choice') == wanted
        if step == 0:
            feedback = ('Aquí se comparan una referencia y una aproximación.' if topic == 'errores' else
                        'Aquí buscamos un valor que anule una función, no varias incógnitas de un sistema.')
        else:
            feedback = ('El error absoluto conserva las unidades; el relativo y porcentual son proporciones.' if topic == 'errores' else
                        'El punto medio corresponde a bisección; los otros métodos construyen otro paso.' if topic == 'biseccion' else
                        METHOD_TASKS[topic][0] + ' Revisa qué datos utiliza cada método.')

    elif step == 2:
        keys = ('a', 'b') if topic in ('biseccion', 'regla-falsa') else ('x0', 'x1') if topic == 'secante' else ('x0',)
        candidate = {key: numeric(payload, key) for key in keys}
        low, high = (data['low'], data['high']) if topic == 'punto-fijo' else (0 if 'a' in keys else .25, 4)
        correct = all(low <= value <= high for value in candidate.values())
        feedback = f'Elige los datos dentro de [{low:g}, {high:g}].' + (' Evita una derivada nula; observa el cruce antes de elegir.' if topic == 'newton' else '')
        if correct:
            try:
                first_iteration(state, candidate)
            except MathInputError as exc:
                correct, feedback = False, str(exc)
        if correct:
            values.update(candidate)
    elif step == 3:
        row = first_iteration(state, {key: value for key, value in values.items() if key != 'x'})
        x = numeric(payload, 'x')
        correct = close(x, row['x'])
        feedback = 'Revisa la sustitución en la fórmula: evalúa cada función en el dato correspondiente, conserva sus signos y redondea al final.'
        if correct:
            values['x'] = row['x']
    else:
        row = first_iteration(state, {key: value for key, value in values.items() if key != 'x'})
        expected = ({'new_a': row['new_a'], 'new_b': row['new_b']} if topic == 'regla-falsa' else
                    {'bound': row['error_bound'] if topic == 'biseccion' else row['error']})
        expected['residual'] = abs(row['fx'])
        for key, wanted in expected.items():
            valid = close(numeric(payload, key), wanted)
            message = ('Correcto.' if valid else
                       'Sustituye la aproximación nueva en la función y toma el valor absoluto. En punto fijo evalúa |g(x) − x|.' if key == 'residual' else
                       'Revisa los signos para conservar el intervalo que encierra la raíz.' if key in ('new_a', 'new_b') else
                       'Usa la semilongitud del intervalo inicial.' if topic == 'biseccion' else
                       'Resta la nueva aproximación y la inmediatamente anterior; toma la magnitud.')
            checks.append({'field': key, 'correct': valid, 'message': message})
        correct = all(item['correct'] for item in checks)
        feedback = 'Revisa los campos indicados; las medidas se comprueban por separado.'
    if correct:
        state['step'] += 1
        feedback = 'Correcto.'
        if state['step'] == 5 and topic == 'errores':
            feedback += f" Ea = {values['x']:g} {'cumple' if values['x'] <= data['tolerance'] else 'no cumple'} la tolerancia {data['tolerance']:g}."
    else:
        state['mistakes'] += 1
    return {'success': True, 'correct': correct, 'feedback': feedback, 'checks': checks, 'state': public_practice(state)}
