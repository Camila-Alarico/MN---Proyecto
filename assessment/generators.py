"""Generadores de problemas paso a paso con datos distintos en cada intento.

Cada generador recibe un `random.Random` sembrado por intento y pregunta, y devuelve:
    {'given': [líneas del enunciado], 'steps': [paso, ...]}
Un paso es {'prompt', 'kind': 'number'|'choice', 'answer', 'options'?, 'explain'}.
El servidor guarda solo la semilla; las respuestas se recalculan al comprobar y nunca viajan al navegador
antes de que el alumno responda (o agote los intentos de ese paso).
"""
import math
from decimal import Decimal, ROUND_DOWN, ROUND_HALF_UP


def n(value):
    """Número legible para enunciados: sin ceros sobrantes ni notación científica."""
    text = f'{value:.6f}'.rstrip('0').rstrip('.')
    return text if text not in ('', '-0') else '0'


def num(prompt, answer, explain, tol=None):
    """`tol` = tolerancia absoluta propia del paso (por defecto el motor usa 0.1 % relativo o 5e-5)."""
    step = {'prompt': prompt, 'kind': 'number', 'answer': float(answer), 'explain': explain}
    if tol is not None:
        step['tol'] = tol
    return step


def eq(coefficients, rhs):
    """Ecuación lineal legible: eq([2, -3], 5) -> '2·x₁ − 3·x₂ = 5'."""
    text = ''
    for i, c in enumerate(coefficients):
        term = f'{abs(c)}·x{"₁₂₃"[i]}'
        text += (('−' if c < 0 else '') + term) if i == 0 else (' − ' if c < 0 else ' + ') + term
    return f'{text} = {str(rhs).replace("-", "−")}'


def choice(prompt, answer, options, explain):
    return {'prompt': prompt, 'kind': 'choice', 'answer': answer, 'options': [list(o) for o in options], 'explain': explain}


YES_NO = [('si', 'Sí'), ('no', 'No')]


# --- Módulo 1: errores -------------------------------------------------------------------------

def error_measures(rng):
    v = rng.choice([20, 25, 40, 50, 80, 125, 200, 250])
    pct = rng.choice([0.5, 1, 2, 2.5, 4, 5])
    approx = round(v * (1 + rng.choice([-1, 1]) * pct / 100), 6)
    ea = abs(v - approx)
    tau = round(ea * rng.choice([0.8, 1.0, 1.25]), 6)
    er = ea / abs(v)
    accepted = ea <= tau + 1e-12
    return {
        'given': [f'Referencia v = {n(v)}', f'Aproximación ṽ = {n(approx)}', f'Tolerancia absoluta τ = {n(tau)}'],
        'steps': [
            num('Calcula el error absoluto Ea.', ea, 'Ea = |v − ṽ|: resta los dos valores y toma la magnitud.'),
            num('Con tu Ea, calcula el error relativo Er (como proporción, sin multiplicar por 100).', er,
                'Er = Ea / |v|. El denominador es la referencia, no la tolerancia.'),
            num('Expresa ese error relativo como error porcentual Ep (solo el número, sin %).', 100 * er,
                'Ep = 100 · Er.'),
            choice('¿Se cumple Ea ≤ τ?', 'si' if accepted else 'no', YES_NO,
                   'Se compara el error absoluto con la tolerancia absoluta; la igualdad también cumple.'),
        ],
    }


def round_vs_truncate(rng):
    k = rng.choice([2, 3])
    discarded = rng.randint(1, 9)
    head = Decimal(rng.randint(100, 999)) / Decimal(100)
    x = (head.quantize(Decimal(1).scaleb(-k)) + Decimal(discarded).scaleb(-(k + 1)) + Decimal(rng.randint(0, 9)).scaleb(-(k + 2)))
    step = Decimal(1).scaleb(-k)
    truncated = x.quantize(step, rounding=ROUND_DOWN)
    rounded = x.quantize(step, rounding=ROUND_HALF_UP)
    e_trunc, e_round = abs(x - truncated), abs(x - rounded)
    better = 'same' if e_trunc == e_round else ('round' if e_round < e_trunc else 'trunc')
    return {
        'given': [f'Valor x = {x}', f'Se conservan {k} decimales.'],
        'steps': [
            num(f'¿Cuánto vale x truncado a {k} decimales?', truncated, 'Truncar descarta las cifras sobrantes sin mirarlas.'),
            num(f'¿Cuánto vale x redondeado a {k} decimales?', rounded,
                'Redondear mira la primera cifra descartada: si es 5 o más, sube la última cifra conservada.'),
            num('Calcula el error absoluto de la versión redondeada: |x − redondeado|.', e_round,
                'Es la distancia entre el valor original y el redondeado.', tol=1e-6),
            choice('¿Qué versión queda más cerca de x?', better,
                   [('trunc', 'El truncado'), ('round', 'El redondeado'), ('same', 'Ambas igual de cerca')],
                   'Compara |x − truncado| con |x − redondeado|. Si la cifra descartada es menor que 5 coinciden.'),
        ],
    }


def same_error_different_scale(rng):
    ea = rng.choice([0.1, 0.2, 0.5, 1, 2])
    small, large = rng.choice([1, 2, 5, 10]), rng.choice([100, 200, 500, 1000])
    a_ref, b_ref = (small, large) if rng.random() < 0.5 else (large, small)
    er_a, er_b = ea / a_ref, ea / b_ref
    return {
        'given': [f'Dos mediciones tienen el mismo error absoluto Ea = {n(ea)}.',
                  f'Medición A: referencia {n(a_ref)}. Medición B: referencia {n(b_ref)}.'],
        'steps': [
            num('Calcula el error relativo de la medición A.', er_a, 'Er = Ea / |referencia|.', tol=1e-6),
            num('Calcula el error relativo de la medición B.', er_b, 'Er = Ea / |referencia|.', tol=1e-6),
            choice('¿Cuál medición es relativamente peor?', 'A' if er_a > er_b else 'B', [('A', 'La A'), ('B', 'La B')],
                   'A igual distancia, la referencia más pequeña produce un error relativo mayor.'),
            num('Expresa el error relativo de la medición A como porcentaje (solo el número).', 100 * er_a, 'Ep = 100 · Er.'),
        ],
    }


# --- Módulo 1: raíces ----------------------------------------------------------------------------

def bisection_step(rng):
    c, a, b = rng.choice([2, 3, 5, 6, 7, 10]), rng.choice([0, 1]), rng.choice([4, 5, 6])
    f = lambda x: x * x - c
    m1 = (a + b) / 2
    side = 'right' if f(m1) < 0 else 'left'
    lo, hi = (m1, b) if side == 'right' else (a, m1)
    return {
        'given': [f'f(x) = x² − {c}', f'Intervalo inicial [{a}, {b}] (f cambia de signo en él).'],
        'steps': [
            num('Calcula el primer punto medio m₁.', m1, 'm = (a + b) / 2.'),
            num('Calcula f(m₁).', f(m1), 'Sustituye m₁ en f(x) = x² − c.'),
            choice('¿Qué subintervalo conservas?', side, [('left', f'[{n(a)}, {n(m1)}]'), ('right', f'[{n(m1)}, {n(b)}]')],
                   'Se conserva el subintervalo donde f cambia de signo: compara el signo de f(m₁) con el de f(a) y f(b).'),
            num('Calcula el segundo punto medio m₂ dentro del intervalo conservado.', (lo + hi) / 2, 'Vuelve a aplicar (a + b) / 2 con los nuevos extremos.'),
            num('Calcula la cota de error (b − a)/2 del intervalo conservado tras la primera iteración.', (hi - lo) / 2,
                'La semilongitud del intervalo conservado acota la distancia del punto medio a la raíz.'),
        ],
    }


def false_position_step(rng):
    c, a, b = rng.choice([2, 3, 5, 6, 7]), 1, rng.choice([3, 4])
    f = lambda x: x * x - c
    xr = a - f(a) * (b - a) / (f(b) - f(a))
    side = 'right' if f(a) * f(xr) > 0 else 'left'
    return {
        'given': [f'f(x) = x² − {c}', f'Intervalo inicial [{a}, {b}].'],
        'steps': [
            num('Calcula f(a).', f(a), 'Sustituye a en f(x).'),
            num('Calcula f(b).', f(b), 'Sustituye b en f(x).'),
            num('Calcula x_r = a − f(a)(b − a) / (f(b) − f(a)).', xr, 'Es el punto donde la recta que une (a, f(a)) y (b, f(b)) corta el eje x.'),
            choice('¿Qué subintervalo conservas?', side, [('left', f'[{n(a)}, {n(xr)}]'), ('right', f'[{n(xr)}, {n(b)}]')],
                   'Evalúa el signo de f(x_r) y conserva el lado donde hay cambio de signo.'),
            num('Calcula el residuo |f(x_r)|.', abs(f(xr)), 'Sustituye x_r en f y toma el valor absoluto.'),
        ],
    }


def fixed_point_step(rng):
    slope = rng.choice([0.4, 0.5, 0.6, -0.5, -0.8, 1.5, 2, -2])
    k, x0 = rng.choice([1, 2, 3, 4]), rng.choice([0, 1, 2])
    g = lambda x: slope * x + k
    x1 = g(x0)
    return {
        'given': [f'g(x) = {n(slope)}·x + {k}', f'Punto inicial x₀ = {x0}.'],
        'steps': [
            num('Calcula x₁ = g(x₀).', x1, 'Sustituye x₀ en g.'),
            num('Calcula x₂ = g(x₁).', g(x1), 'Repite el paso con la aproximación anterior.'),
            num('¿Cuánto vale |g′(x)|? (g es una recta: la pendiente no cambia).', abs(slope), 'La derivada de a·x + k es a.'),
            choice('Según |g′|, ¿la iteración converge?', 'si' if abs(slope) < 1 else 'no', YES_NO,
                   'Con |g′| < 1 la iteración es una contracción y converge; con |g′| > 1 se aleja del punto fijo.'),
            num('¿Cuánto vale el punto fijo p, donde g(p) = p?', k / (1 - slope), 'Resuelve a·p + k = p, es decir, p = k / (1 − a).'),
        ],
    }


def newton_step(rng):
    c, x0 = rng.choice([2, 3, 5, 7, 10]), rng.choice([2, 3, 4])
    f = lambda x: x * x - c
    x1 = x0 - f(x0) / (2 * x0)
    return {
        'given': [f'f(x) = x² − {c}', 'f′(x) = 2x', f'Punto inicial x₀ = {x0}.'],
        'steps': [
            num('Calcula f(x₀).', f(x0), 'Sustituye x₀ en f.'),
            num('Calcula f′(x₀).', 2 * x0, 'Sustituye x₀ en la derivada.'),
            num('Calcula x₁ = x₀ − f(x₀)/f′(x₀).', x1, 'Usa los dos valores de los pasos anteriores.'),
            num('Calcula el tamaño del paso |x₁ − x₀|.', abs(x1 - x0), 'Es la distancia entre dos aproximaciones consecutivas.'),
            num('Calcula el residuo |f(x₁)|.', abs(f(x1)), 'Sustituye x₁ en f y toma el valor absoluto.'),
        ],
    }


def secant_step(rng):
    c, x0, x1 = rng.choice([2, 3, 5, 6]), 1, rng.choice([2, 3])
    f = lambda x: x * x - c
    x2 = x1 - f(x1) * (x1 - x0) / (f(x1) - f(x0))
    return {
        'given': [f'f(x) = x² − {c}', f'Puntos iniciales x₀ = {x0} y x₁ = {x1}.'],
        'steps': [
            num('Calcula f(x₀).', f(x0), 'Sustituye x₀ en f.'),
            num('Calcula f(x₁).', f(x1), 'Sustituye x₁ en f.'),
            num('Calcula x₂ = x₁ − f(x₁)(x₁ − x₀) / (f(x₁) − f(x₀)).', x2, 'La recta secante sustituye a la tangente; no hace falta f′.'),
            num('Calcula el residuo |f(x₂)|.', abs(f(x2)), 'Sustituye x₂ en f y toma el valor absoluto.'),
        ],
    }


# --- Módulo 2: sistemas lineales -----------------------------------------------------------------

def gauss_pivot_2x2(rng):
    while True:
        big, small = rng.choice([5, 6, 8]), rng.choice([1, 2, 3])
        a12, a22 = rng.choice([1, 2, 3, -1, -2]), rng.choice([2, 3, 4, -2, -3])
        rows = [[small, a12], [big, a22]] if rng.random() < 0.75 else [[big, a12], [small, a22]]
        if rows[0][0] * rows[1][1] - rows[0][1] * rows[1][0] != 0:
            break
    sol = [rng.randint(-3, 4), rng.randint(-3, 4)]
    b = [r[0] * sol[0] + r[1] * sol[1] for r in rows]
    p = 0 if abs(rows[0][0]) >= abs(rows[1][0]) else 1
    o = 1 - p
    m = rows[o][0] / rows[p][0]
    a22n = rows[o][1] - m * rows[p][1]
    x2 = (b[o] - m * b[p]) / a22n
    x1 = (b[p] - rows[p][1] * x2) / rows[p][0]
    return {
        'given': [f'F1: {eq(rows[0], b[0])}', f'F2: {eq(rows[1], b[1])}', 'Redondea a 4 decimales si hace falta.'],
        'steps': [
            choice('¿Qué fila usas como pivote de la columna 1 (pivoteo parcial)?', f'F{p + 1}', [('F1', 'F1'), ('F2', 'F2')],
                   'El pivoteo parcial elige la fila con mayor |a_i1| para evitar multiplicadores grandes.'),
            num('Con esa fila de pivote, calcula el multiplicador m = a_otra,1 / pivote.', m, 'Es el cociente entre el elemento a eliminar y el pivote.'),
            num('Tras restar m veces la fila pivote, ¿cuánto vale el nuevo coeficiente de x₂ en la otra fila?', a22n, 'Nuevo a = a_otra,2 − m · a_pivote,2.'),
            num('Calcula x₂ con la fila reducida.', x2, 'x₂ = (b_otra − m · b_pivote) / nuevo coeficiente.'),
            num('Sustituye hacia atrás: calcula x₁.', x1, 'Despeja x₁ en la fila pivote usando x₂.'),
        ],
    }


def gauss_back_substitution(rng):
    sol = [rng.randint(-3, 4) for _ in range(3)]
    u = [[rng.choice([1, 2, 3, 4]), rng.randint(-3, 3), rng.randint(-3, 3)],
         [0, rng.choice([1, 2, 3, 5]), rng.randint(-3, 3)],
         [0, 0, rng.choice([1, 2, 4, 5])]]
    b = [sum(u[i][j] * sol[j] for j in range(3)) for i in range(3)]
    lines = [eq(u[i], b[i]) for i in range(3)]
    return {
        'given': ['Sistema triangular superior (ya eliminado):'] + [f'F{i + 1}: {t}' for i, t in enumerate(lines)],
        'steps': [
            num('Calcula x₃ con la última fila.', sol[2], 'La última fila solo tiene x₃.'),
            num('Calcula x₂ con la segunda fila y tu x₃.', sol[1], 'Despeja x₂ y sustituye x₃.'),
            num('Calcula x₁ con la primera fila.', sol[0], 'Despeja x₁ y sustituye x₂ y x₃.'),
            num('Si alguien propone x̃ = (x₁ + 1, x₂, x₃), ¿cuánto vale el residuo |b₁ − (fila 1 · x̃)| de la primera ecuación?', abs(u[0][0]),
                'Cambiar x₁ en 1 altera la primera ecuación en a₁₁ unidades.'),
        ],
    }


def seidel_step(rng):
    a11, a22 = rng.choice([4, 5, 6, 8]), rng.choice([4, 5, 7, 9])
    a12, a21 = rng.randint(-3, 3), rng.randint(-3, 3)
    if rng.random() < 0.35:
        a12 = a11 + rng.choice([1, 2])
    b1, b2 = rng.randint(1, 20), rng.randint(1, 20)
    dominant = abs(a11) > abs(a12) and abs(a22) > abs(a21)
    x1 = b1 / a11
    x2 = (b2 - a21 * x1) / a22
    r1 = b1 - a11 * x1 - a12 * x2
    return {
        'given': [f'F1: {eq([a11, a12], b1)}', f'F2: {eq([a21, a22], b2)}',
                  'Vector inicial x⁽⁰⁾ = (0, 0). Redondea a 4 decimales si hace falta.'],
        'steps': [
            choice('¿La matriz es estrictamente diagonal dominante por filas?', 'si' if dominant else 'no', YES_NO,
                   'Se comprueba |a_ii| > Σ|a_ij| (j ≠ i) en cada fila.'),
            num('Calcula x₁⁽¹⁾ despejando x₁ de F1 con x₂ = 0.', x1, 'x₁ = (b₁ − a₁₂·x₂) / a₁₁ con x₂ = 0.'),
            num('Calcula x₂⁽¹⁾ despejando x₂ de F2 con el x₁⁽¹⁾ recién calculado.', x2, 'Gauss-Seidel usa de inmediato el valor ya actualizado de x₁.'),
            num('Calcula el tamaño del paso ‖x⁽¹⁾ − x⁽⁰⁾‖∞.', max(abs(x1), abs(x2)), 'Es la mayor diferencia en valor absoluto entre componentes; x⁽⁰⁾ = 0.'),
            num('Calcula el residuo en valor absoluto de la primera ecuación: |b₁ − a₁₁x₁ − a₁₂x₂| con x⁽¹⁾.', abs(r1), 'Sustituye x⁽¹⁾ en F1, resta de b₁ y toma la magnitud.'),
        ],
    }


# --- Módulo 1 · errores: generadores adicionales (banco de 50 preguntas) ---------------------------

def tolerance_relative(rng):
    v = rng.choice([40, 50, 80, 125, 200, 250])
    pct = rng.choice([1, 2, 2.5, 4, 5])
    approx = round(v * (1 + rng.choice([-1, 1]) * pct / 100), 6)
    limit = round(pct * rng.choice([0.8, 1.0, 1.25]), 4)
    ea = abs(v - approx)
    return {
        'given': [f'Referencia v = {n(v)}', f'Aproximación ṽ = {n(approx)}', f'Tolerancia relativa: {n(limit)} %'],
        'steps': [
            num('Calcula el error absoluto Ea.', ea, 'Ea = |v − ṽ|.'),
            num('Calcula el error porcentual Ep (solo el número).', 100 * ea / v, 'Ep = 100 · Ea / |v|.'),
            num('Convierte la tolerancia relativa en una tolerancia absoluta τ = |v| · tolerancia / 100.', v * limit / 100,
                'Una tolerancia relativa se convierte en absoluta multiplicando por |v|.', tol=1e-6),
            choice('¿La aproximación cumple la tolerancia?', 'si' if 100 * ea / v <= limit + 1e-9 else 'no', YES_NO,
                   'Compara el error porcentual con la tolerancia en %, o Ea con la τ absoluta equivalente: el resultado es el mismo.'),
        ],
    }


def propagation_sum(rng):
    while True:
        a, b = rng.choice([12.5, 20, 32.4, 48]), rng.choice([8.2, 15, 27.6, 40])
        ea, eb = rng.choice([0.05, 0.1, 0.2, 0.5]), rng.choice([0.05, 0.1, 0.2, 0.5])
        if ea != eb:
            break
    total, bound = round(a + b, 6), round(ea + eb, 6)
    return {
        'given': [f'Tramo A = {n(a)} ± {n(ea)} m', f'Tramo B = {n(b)} ± {n(eb)} m',
                  'El error absoluto máximo de una suma es la suma de los errores absolutos máximos.'],
        'steps': [
            num('Calcula la longitud total A + B.', total, 'Se suman los valores medidos.'),
            num('Calcula el error absoluto máximo de la suma.', bound, 'Los errores absolutos de los sumandos se suman.', tol=1e-6),
            num('Calcula el error relativo máximo de la suma, en % (solo el número).', 100 * bound / total, 'Er = Ea / |valor|, multiplicado por 100 para el porcentaje.'),
            choice('¿Qué tramo aporta más al error absoluto de la suma?', 'A' if ea > eb else 'B', [('A', 'El tramo A'), ('B', 'El tramo B')],
                   'Aporta más el que tiene mayor error absoluto máximo, aunque no sea el más largo.'),
        ],
    }


def cancellation(rng):
    a = rng.choice([50.4, 80.6, 120.3, 250.8])
    delta = rng.choice([0.4, 0.5, 0.6, 0.8])
    b = round(a - delta, 1)
    e = rng.choice([0.02, 0.05, 0.1])
    diff, bound = round(a - b, 6), round(2 * e, 6)
    return {
        'given': [f'Medición A = {n(a)} ± {n(e)}', f'Medición B = {n(b)} ± {n(e)}', 'Se calcula la diferencia A − B.'],
        'steps': [
            num('Calcula la diferencia A − B.', diff, 'Restar los dos valores medidos.', tol=1e-6),
            num('Calcula el error relativo de la medición A, en % (solo el número).', 100 * e / a, 'Er = error absoluto / |valor|; después × 100.'),
            num('Calcula el error absoluto máximo de la diferencia.', bound, 'Al restar, los errores absolutos máximos también se suman.', tol=1e-6),
            num('Calcula el error relativo máximo de la diferencia, en % (solo el número).', 100 * bound / diff, 'Se divide entre la diferencia, que es pequeña.'),
            choice('Comparado con el de A, el error relativo de la diferencia…', 'amplifica',
                   [('amplifica', 'Se amplificó'), ('igual', 'Quedó igual'), ('reduce', 'Se redujo')],
                   'Restar cantidades casi iguales deja un resultado pequeño con el mismo error absoluto: el error relativo crece.'),
        ],
    }


def reference_zero(rng):
    approx = rng.choice([0.0003, 0.002, -0.0015, 0.0008])
    tau = rng.choice([0.001, 0.0005, 0.002])
    ea = abs(approx)
    return {
        'given': ['Referencia v = 0', f'Aproximación ṽ = {n(approx)}', f'Tolerancia absoluta τ = {n(tau)}'],
        'steps': [
            num('Calcula el error absoluto Ea.', ea, 'Ea = |0 − ṽ| = |ṽ|.', tol=1e-9),
            choice('¿Está definido el error relativo Er = Ea/|v|?', 'no', YES_NO, 'Habría que dividir entre |v| = 0: no está definido.'),
            choice('¿Se cumple Ea ≤ τ?', 'si' if ea <= tau + 1e-12 else 'no', YES_NO,
                   'La comparación con una tolerancia absoluta sigue siendo posible aunque el relativo no exista.'),
            choice('Un compañero escribe «Er = 0». ¿Es correcto?', 'no', [('no', 'No: no está definido, no vale cero'), ('si', 'Sí: el error relativo vale cero')],
                   'No definido no significa cero: Er = 0 diría que la aproximación es exacta, y aquí no lo es.'),
        ],
    }


def negative_reference(rng):
    v = rng.choice([-5, -12, -40, -250])
    pct = rng.choice([1, 2, 4, 5])
    approx = round(v * (1 + rng.choice([-1, 1]) * pct / 100), 6)
    ea = abs(v - approx)
    return {
        'given': [f'Referencia v = {n(v)}', f'Aproximación ṽ = {n(approx)}'],
        'steps': [
            num('Calcula el error absoluto Ea.', ea, 'Ea = |v − ṽ|; nunca es negativo.'),
            num('Calcula el error relativo Er = Ea/|v|.', ea / abs(v), 'Se divide entre el valor absoluto de la referencia.'),
            num('Calcula el error porcentual Ep (solo el número).', 100 * ea / abs(v), 'Ep = 100 · Er.'),
            choice('¿Puede salir negativo el error relativo con esta definición?', 'no', YES_NO,
                   'Con Ea ≥ 0 y |v| > 0, el cociente no es negativo aunque la referencia lo sea.'),
        ],
    }


def two_instruments(rng):
    while True:
        va, pa = rng.choice([1, 2, 4, 5]), rng.choice([4, 5, 8, 10])
        vb, pb = rng.choice([100, 200, 500, 1000]), rng.choice([0.2, 0.5, 1])
        ea, eb = va * pa / 100, vb * pb / 100
        if eb > ea:
            break
    return {
        'given': [f'Instrumento A: referencia {n(va)}, aproximación {n(va - ea)}', f'Instrumento B: referencia {n(vb)}, aproximación {n(vb - eb)}'],
        'steps': [
            num('Calcula el error absoluto del instrumento A.', ea, 'Ea = |v − ṽ|.', tol=1e-6),
            num('Calcula el error absoluto del instrumento B.', eb, 'Ea = |v − ṽ|.', tol=1e-6),
            choice('¿Qué instrumento tiene menor error absoluto?', 'A', [('A', 'El A'), ('B', 'El B')], 'Compara los dos Ea calculados.'),
            num('Calcula el error relativo del instrumento A, en % (solo el número).', pa, 'Er = Ea/|v|; × 100.'),
            num('Calcula el error relativo del instrumento B, en % (solo el número).', pb, 'Er = Ea/|v|; × 100.'),
            choice('¿Qué instrumento es más preciso en proporción a lo que mide?', 'B', [('A', 'El A'), ('B', 'El B')],
                   'El menor error relativo: un error absoluto grande puede ser pequeño frente a una referencia grande.'),
        ],
    }


def series_truncation(rng):
    x = rng.choice([0.5, 1, 1.5, 2])
    terms = rng.choice([3, 4, 5, 6])
    reference = round(math.exp(x), 9)
    partial = sum(x ** k / math.factorial(k) for k in range(terms))
    ea = reference - partial
    return {
        'given': [f'Referencia e^{n(x)} = {reference}',
                  f'Se conservan los primeros {terms} términos de la serie e^x = Σ x^k / k! (k = 0, 1, 2, …), con x = {n(x)}.'],
        'steps': [
            num(f'Calcula la suma de los primeros {terms} términos (k = 0 hasta {terms - 1}).', partial,
                'Suma 1 + x + x²/2! + … con los términos indicados.', tol=1e-6),
            num('Calcula el error absoluto Ea = |referencia − suma|.', ea, 'Resta la suma parcial a la referencia.', tol=1e-6),
            num('Calcula el error porcentual Ep (solo el número).', 100 * ea / reference, 'Ep = 100 · Ea / |referencia|.', tol=1e-4),
            choice('¿De qué tipo es este error?', 'trunc',
                   [('trunc', 'Truncamiento: se cortó una serie infinita'), ('round', 'Redondeo: se limitaron los decimales'), ('prop', 'Propagación de datos')],
                   'Sustituir un proceso infinito por uno finito introduce error de truncamiento.'),
        ],
    }


def rounding_bound(rng):
    k = rng.choice([1, 2, 3])
    while True:
        x = Decimal(str(round(rng.uniform(1, 9), k + 2)))
        digits = f'{x:.{k + 2}f}'
        if not (digits[-2] == '5' and digits[-1] == '0'):
            break
    step = Decimal(1).scaleb(-k)
    rounded = x.quantize(step, rounding=ROUND_HALF_UP)
    return {
        'given': [f'Valor x = {x:.{k + 2}f}', f'Se redondea a {k} decimal{"es" if k > 1 else ""}.'],
        'steps': [
            num(f'¿Cuánto vale x redondeado a {k} decimal{"es" if k > 1 else ""}?', rounded, 'Se mira la primera cifra descartada: 5 o más sube la última conservada.', tol=1e-9),
            num('Calcula el error absoluto de ese redondeo |x − redondeado|.', abs(x - rounded), 'Es la distancia entre el valor original y el redondeado.', tol=1e-9),
            num(f'Calcula la cota máxima de un redondeo a {k} decimal{"es" if k > 1 else ""}: 0.5 · 10^(−{k}).', 0.5 * 10 ** -k,
                'Al redondear, la diferencia nunca supera media unidad de la última cifra conservada.', tol=1e-9),
            choice('¿El error de este redondeo cumple Ea ≤ cota?', 'si', YES_NO, 'Un redondeo correcto siempre queda dentro de media unidad de la última cifra.'),
        ],
    }


def percent_to_absolute(rng):
    v = rng.choice([40, 80, 120, 250])
    pct = rng.choice([0.5, 1, 2, 5])
    below = rng.random() < 0.5
    ea = v * pct / 100
    approx = v - ea if below else v + ea
    tau = round(ea * rng.choice([0.8, 1.25]), 6)
    return {
        'given': [f'Referencia v = {n(v)}', f'La aproximación queda {"por debajo" if below else "por encima"} con un error porcentual de {n(pct)} %.',
                  f'Tolerancia absoluta τ = {n(tau)}'],
        'steps': [
            num('Calcula el error absoluto Ea a partir del porcentaje: Ea = |v| · Ep / 100.', ea, 'Se invierte la definición Ep = 100 · Ea / |v|.', tol=1e-6),
            num('Calcula el valor aproximado ṽ.', approx, 'Resta Ea si queda por debajo de la referencia y súmalo si queda por encima.', tol=1e-6),
            num('Calcula el error relativo Er (como proporción).', pct / 100, 'Er = Ep / 100.', tol=1e-9),
            choice('¿Se cumple Ea ≤ τ?', 'si' if ea <= tau + 1e-12 else 'no', YES_NO, 'Compara el Ea que obtuviste con la tolerancia absoluta.'),
        ],
    }


# --- Unidades nuevas: aproximación, ajuste, integración/derivación y EDO -------------------------

def approximation_taylor(rng):
    x = rng.choice([0.05, 0.1, 0.15, 0.2, 0.25, 0.3, 0.35, 0.4])
    exact = math.exp(x)
    p2 = 1 + x + x*x/2
    return {'given': [f'Aproxima e^{n(x)} con P₂(x) = 1 + x + x²/2.'], 'steps': [
        num('Calcula el término lineal x.', x, 'El término lineal es el propio valor de x.'),
        num('Calcula x²/2.', x*x/2, 'Eleva x al cuadrado y divide entre dos.'),
        num('Calcula P₂(x).', p2, 'Suma 1 + x + x²/2.'),
        num('Calcula el error absoluto frente a eˣ (usa el valor de referencia indicado por la calculadora).', abs(exact-p2), 'El error de truncamiento es |eˣ − P₂(x)|.', tol=1e-6)]}

def approximation_rounding(rng):
    x = rng.choice([math.sqrt(2), math.pi, math.e, math.sqrt(3), math.log(2), math.sqrt(5), math.log(3), math.sqrt(7)])
    approx = round(x, 3)
    return {'given': [f'Valor de referencia x ≈ {x:.8f}.', 'Se conservarán tres decimales.'], 'steps': [
        num('Escribe x redondeado a tres decimales.', approx, 'Se observa la cuarta cifra decimal para decidir el redondeo.', tol=1e-6),
        num('Calcula el error absoluto de la aproximación.', abs(x-approx), 'Ea = |valor de referencia − aproximación|.', tol=1e-6),
        choice('¿La aproximación tiene tres decimales necesariamente mayor exactitud que otra con menos?', 'no', YES_NO, 'La cantidad de decimales mostrados no determina por sí sola la exactitud.')]}

def curve_least_squares(rng):
    slope, intercept = rng.choice([1, 2, 3]), rng.choice([1, 2, 4])
    noise = [rng.choice([-1, 0, 1]) for _ in range(3)]
    xs = [0, 1, 2]
    ys = [slope*x + intercept + e for x, e in zip(xs, noise)]
    sx, sy = sum(xs), sum(ys)
    sxx, sxy = sum(x*x for x in xs), sum(x*y for x, y in zip(xs, ys))
    m = (3*sxy - sx*sy) / (3*sxx - sx*sx)
    c = (sy - m*sx) / 3
    x_eval = 1.5
    return {'given': [f'Datos experimentales: (0, {ys[0]}), (1, {ys[1]}), (2, {ys[2]}).',
                      'Ajusta una recta y = mx + c por mínimos cuadrados.'], 'steps': [
        num('Calcula la suma Σy.', sy, 'Suma las tres ordenadas.'),
        num('Calcula la suma Σxy.', sxy, 'Multiplica cada x por su y y suma los productos.'),
        num('Calcula la pendiente m = (3Σxy − ΣxΣy)/(3Σx² − (Σx)²).', m,
            'Aplica la fórmula de mínimos cuadrados para la pendiente.'),
        num('Calcula la ordenada c = (Σy − mΣx)/3.', c, 'Sustituye la pendiente en la fórmula de la ordenada.'),
        num(f'Predice y para x = {n(x_eval)}.', m*x_eval+c, 'Evalúa la recta ajustada en el valor solicitado.') ]}

def curve_interpolation(rng):
    x0 = rng.choice([1,2,3]); slope = rng.choice([2,3,4]); intercept = rng.choice([1,2])
    x = x0 + 1
    return {'given': [f'Puntos conocidos de una función lineal: ({x0}, {slope*x0+intercept}) y ({x0+2}, {slope*(x0+2)+intercept}).', f'Estima el valor en x = {x}.'], 'steps': [
        num('Calcula la pendiente entre los dos puntos.', slope, 'm = (y₂ − y₁)/(x₂ − x₁).'),
        num('Calcula el valor interpolado en el punto medio.', slope*x+intercept, 'En una recta, el punto medio en x corresponde al promedio de las ordenadas.'),
        choice('¿La interpolación lineal usa valores dentro del intervalo de datos?', 'si', YES_NO, 'La interpolación estima dentro del rango conocido; fuera de él sería extrapolación.')] }

def integration_trapezoid(rng):
    a, b = 0, rng.choice([2,4,6]); fa, fb = rng.choice([1,2]), rng.choice([3,4,5])
    h=b-a; area=h*(fa+fb)/2
    return {'given': [f'Un intervalo [0, {b}] tiene valores f(0) = {fa} y f({b}) = {fb}.', 'Usa una sola aplicación de la regla trapezoidal.'], 'steps': [
        num('Calcula la anchura h = b − a.', h, 'Resta los extremos del intervalo.'),
        num('Calcula el promedio de las alturas.', (fa+fb)/2, 'Promedia f(a) y f(b).'),
        num('Calcula el área aproximada del trapecio.', area, 'I ≈ h·(f(a)+f(b))/2.')]}

def differentiation_central(rng):
    x, h = rng.choice([1,2]), rng.choice([0.1,0.2,0.5])
    # f(x)=x^2; diferencia central exacta para esta función
    deriv=2*x
    return {'given': [f'f(x) = x², x = {x}, h = {n(h)}.', 'Usa la diferencia central.'], 'steps': [
        num('Calcula f(x + h).', (x+h)**2, 'Sustituye x+h en la función.'),
        num('Calcula f(x − h).', (x-h)**2, 'Sustituye x−h en la función.'),
        num('Calcula [f(x+h) − f(x−h)]/(2h).', deriv, 'La fórmula de diferencia central aproxima la derivada primera.', tol=1e-6)]}

def edo_euler(rng):
    y0, x0, h, rate = rng.choice([1,2,3]), 0, rng.choice([0.1,0.2,0.5]), rng.choice([1,2])
    y1=y0+h*rate*y0
    return {'given': [f"Problema y' = {rate}y, y(0) = {y0}.", f'Paso h = {n(h)}.'], 'steps': [
        num("Evalúa la pendiente y' en el punto inicial.", rate*y0, 'Sustituye y₀ en f(x,y) = rate·y.'),
        num('Calcula y₁ con Euler: y₁ = y₀ + h·f(x₀,y₀).', y1, 'Suma al valor actual el paso por la pendiente.'),
        choice('¿Euler utiliza la pendiente evaluada al inicio del intervalo?', 'si', YES_NO, 'Euler explícito usa una sola pendiente, evaluada en el extremo inicial.')]}

def edo_rk2(rng):
    y0, h, rate = rng.choice([1,2]), rng.choice([0.1,0.2]), rng.choice([1,2])
    k1=rate*y0; k2=rate*(y0+h*k1); y1=y0+h*(k1+k2)/2
    return {'given': [f"Problema y' = {rate}y, y(0) = {y0}.", f'Paso h = {n(h)}.', 'Usa Euler modificado (Heun).'], 'steps': [
        num('Calcula k₁ = f(x₀,y₀).', k1, 'Evalúa la pendiente inicial.'),
        num('Calcula k₂ = f(x₀+h, y₀+h·k₁).', k2, 'Evalúa la pendiente en el predictor.'),
        num('Calcula y₁ = y₀ + h(k₁+k₂)/2.', y1, 'Promedia las pendientes inicial y predicha.')]}
