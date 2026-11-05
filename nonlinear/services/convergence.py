"""Criterios de convergencia y divergencia evaluados sobre la propia función.

Métodos de un punto, xₙ₊₁ = φ(xₙ) (punto fijo, Newton, raíces múltiples): si φ(x*) = x* y
|φ′(x*)| < 1, existe un entorno de x* donde la iteración converge; si |φ′(x*)| > 1 la iteración se
aleja de x*. Aquí φ′ se deriva simbólicamente y se evalúa en una malla, de modo que la región de
contracción (|φ′| < 1) puede dibujarse sobre la función en lugar de mostrar solo un aviso.

Métodos cerrados (bisección, regla falsa): el teorema del valor intermedio garantiza la raíz si f es
continua y f(a)·f(b) < 0. Secante: convergencia local de orden (1+√5)/2 si f′(x*) ≠ 0.

Además cada análisis incluye `checks`: comprobaciones automáticas de que las fórmulas empleadas
están bien planteadas (derivada simbólica frente a diferencias finitas, equivalencia g ↔ f,
cambio de signo, dominio de evaluación).
"""
import math

import sympy as sp

from .parser import X, MathInputError

CURVE_POINTS = 161
CURVE_CLAMP = 4.0  # |φ′| se recorta a este valor solo para dibujar; el criterio usa el valor real
ONE_POINT = ('fixed-point', 'newton', 'multiple-roots')
GOLDEN = (1 + 5 ** 0.5) / 2


def fast_function(expression):
    """Convierte una expresión SymPy ya validada por el parser en una función float rápida.

    `expression` nunca es texto del usuario: sale del AST restringido de `parse_function`.
    Devuelve None cuando el valor no es real y finito (dominio, desbordamiento, complejo).
    """
    compiled = sp.lambdify(X, expression, modules=['math'])

    def call(x):
        try:
            value = float(compiled(x))
        except (ValueError, TypeError, OverflowError, ZeroDivisionError):
            return None
        return value if math.isfinite(value) else None
    return call


def _safe(function, x):
    try:
        return function(x)
    except MathInputError:
        return None


def _phi(method, expr):
    """Función de iteración φ(x) del método, o None si no es de un solo punto."""
    if method == 'fixed-point':
        return expr
    d1 = sp.diff(expr, X)
    if method == 'newton':
        return X - expr / d1
    if method == 'multiple-roots':
        d2 = sp.diff(expr, X, 2)
        return X - expr * d1 / (d1 ** 2 - expr * d2)
    return None


def _dphi(method, expr, phi):
    """φ′(x). Newton usa la forma cerrada f·f″/(f′)² (sin cancelaciones cerca de la raíz)."""
    if method == 'newton':
        return expr * sp.diff(expr, X, 2) / sp.diff(expr, X) ** 2
    return sp.diff(phi, X)


def _tex(expr, limit=320):
    text = sp.latex(expr)
    return text if len(text) <= limit else None  # expresiones enormes no se muestran


def _check(ok, label, detail):
    return {'ok': ok, 'label': label, 'detail': detail}


def _derivative_check(expr, order, points, label):
    """Compara la derivada simbólica con una diferencia central en varios puntos."""
    base = fast_function(expr)
    exact = fast_function(sp.diff(expr, X, order))
    worst, used = 0.0, 0
    for x in points:
        h = 1e-4 * max(1.0, abs(x)) if order == 2 else 1e-6 * max(1.0, abs(x))
        if order == 1:
            values = [base(x + h), base(x - h)]
            numeric = None if None in values else (values[0] - values[1]) / (2 * h)
        else:
            values = [base(x + h), base(x), base(x - h)]
            numeric = None if None in values else (values[0] - 2 * values[1] + values[2]) / (h * h)
        symbolic = exact(x)
        if numeric is None or symbolic is None:
            continue
        worst = max(worst, abs(numeric - symbolic) / (1 + abs(symbolic)))
        used += 1
    if not used:
        return _check(None, label, 'No hay puntos donde evaluar ambas derivadas.')
    tolerance = 1e-3 if order == 2 else 1e-5
    return _check(worst <= tolerance, label,
                  f'Discrepancia relativa máxima entre derivada exacta y diferencias finitas: {worst:.2e} en {used} puntos.')


def _domain_check(function, low, high):
    points = [low + (high - low) * i / 8 for i in range(9)]
    failed = sum(1 for x in points if function(x) is None)
    return _check(failed == 0, 'Dominio de la función en la región del recorrido',
                  'Se evaluó en 9 puntos sin problemas.' if not failed
                  else f'{failed} de 9 puntos no dan un valor real finito; revisa el dominio.')


def _domain(iterates, root, cleaned):
    """Intervalo x donde se dibuja el criterio: alrededor de los iterados, la raíz y los datos."""
    points = [x for x in iterates if abs(x) <= 1e6]
    if root is not None and abs(root) <= 1e6:
        points.append(root)
    points += [cleaned[k] for k in ('a', 'b', 'x0', 'x1') if cleaned.get(k) is not None]
    low, high = min(points), max(points)
    if high - low < 1e-9:
        low, high = low - 1, high + 1
    pad = max(0.35 * (high - low), 0.5)
    return low - pad, high + pad


def _local_value(dphi, root, iterates):
    """|φ′| en la raíz; si allí es 0/0 (raíz múltiple exacta) se usa el último iterado."""
    if root is not None:
        value = dphi(root)
        if value is not None:
            return abs(value), 'en x*'
    for x in reversed(iterates):
        if root is not None and x == root:
            continue
        value = dphi(x)
        if value is not None:
            return abs(value), 'en el último iterado'
    return None, None


def analyze(method, iter_f, f, root, iterates, cleaned, tol, precise_root):
    """Análisis de convergencia de `method`.

    iter_f: función iterada (g para punto fijo, f en los demás); f: la ecuación f(x) = 0;
    root: raíz de referencia (o None); iterates: aproximaciones del recorrido.
    """
    if method in ONE_POINT:
        return _analyze_one_point(method, iter_f, f, root, iterates, cleaned, tol, precise_root)
    if method in ('bisection', 'false-position'):
        return _analyze_bracket(method, f, cleaned)
    return _analyze_secant(f, root, iterates, cleaned)


def _analyze_one_point(method, iter_f, f, root, iterates, cleaned, tol, precise_root):
    expr = iter_f.expression
    info = {'kind': 'contraction', 'verdict': 'inconclusive', 'criterion_tex': r"|\varphi'(x^{*})| < 1",
            'formula_tex': {
                'fixed-point': r"\varphi(x)=g(x),\qquad \varphi'(x)=g'(x)",
                'newton': r"\varphi(x)=x-\frac{f(x)}{f'(x)},\qquad \varphi'(x)=\frac{f(x)\,f''(x)}{[f'(x)]^{2}}",
                'multiple-roots': r"\varphi(x)=x-\frac{f f'}{(f')^{2}-f f''}",
            }[method], 'dphi_tex': None, 'lambda': None, 'lambda_at': None, 'curve': None,
            'iterates': [], 'order': None, 'text': '', 'checks': []}
    try:
        phi = _phi(method, expr)
        dphi_expr = _dphi(method, expr, phi)
        if dphi_expr.has(sp.Derivative, sp.DiracDelta):
            raise MathInputError('La derivada no es regular; evita abs en este criterio.')
    except MathInputError as exc:
        info['text'] = str(exc)
        return info
    dphi = fast_function(dphi_expr)
    info['dphi_tex'] = _tex(dphi_expr)

    # --- Fórmulas bien planteadas ---
    checks = info['checks']
    sample = [x for x in (iterates[:1] + [root]) if x is not None]
    checks.append(_derivative_check(f.expression if method != 'fixed-point' else expr, 1, sample,
                                    "Derivada de g(x)" if method == 'fixed-point' else "Derivada f′(x)"))
    if method == 'multiple-roots':
        checks.append(_derivative_check(expr, 2, sample, 'Segunda derivada f″(x)'))
    low, high = _domain(iterates, root, cleaned)
    checks.append(_domain_check(fast_function(expr), low, high))
    if method == 'fixed-point' and root is not None:
        g_value = fast_function(expr)(root)
        limit = (1e-9 if precise_root else max(tol, 1e-9)) * (1 + abs(root))
        if g_value is None:
            checks.append(_check(None, 'g(x) equivalente a f(x) = 0', 'g no se puede evaluar en la raíz de f.'))
        else:
            gap = abs(g_value - root)
            checks.append(_check(gap <= limit, 'g(x) equivalente a f(x) = 0',
                                 f'En la raíz x* de f: |g(x*) − x*| = {gap:.2e} '
                                 + ('(cumple x* = g(x*)).' if gap <= limit
                                    else '> 0. El punto fijo de g no es la raíz de f: g está mal planteada.')))
    if method in ('newton', 'multiple-roots') and root is not None:
        slope = _safe(f.derivative(), root)
        if slope is not None and abs(slope) < 1e-6:
            checks.append(_check(method == 'multiple-roots', 'Raíz simple (f′(x*) ≠ 0)',
                                 'f′(x*) ≈ 0: es una raíz múltiple. '
                                 + ('Newton modificado es el método adecuado.' if method == 'multiple-roots'
                                    else 'Newton pierde el orden 2 (converge linealmente); usa Raíces múltiples.')))

    # --- Criterio |φ′| < 1 evaluado sobre la función ---
    lam, where = _local_value(dphi, root, iterates)
    info['lambda'], info['lambda_at'] = lam, where
    xs = [low + (high - low) * i / (CURVE_POINTS - 1) for i in range(CURVE_POINTS)]
    ys = [None if (v := dphi(x)) is None else min(abs(v), CURVE_CLAMP) for x in xs]
    info['curve'] = {'x': xs, 'y': ys, 'clamp': CURVE_CLAMP}
    for n, x in enumerate(iterates):
        value = dphi(x) if low <= x <= high else None
        info['iterates'].append({'n': n, 'x': x, 'y': None if value is None else min(abs(value), CURVE_CLAMP)})
    inside = [p for p in info['iterates'] if p['y'] is not None]
    info['fraction_contracting'] = (sum(1 for p in inside if p['y'] < 1) / len(inside)) if inside else None

    if lam is None:
        info['text'] = 'No se pudo evaluar φ′ cerca de la raíz.'
        return info
    if lam < 1 - 1e-9:
        info['verdict'] = 'converge'
        if method == 'fixed-point':
            info['order'] = {'p': 2 if lam < 1e-9 else 1,
                             'label': 'superlineal' if lam < 1e-9 else f'lineal, factor ≈ {lam:.4g}'}
        elif lam < 1e-6:
            info['order'] = {'p': 2, 'label': 'cuadrática (raíz simple)'}
        else:
            info['order'] = {'p': 1, 'label': f'lineal, factor ≈ {lam:.4g} (raíz múltiple)'}
        info['text'] = (f'|φ′| = {lam:.4g} < 1 {where}: la iteración converge localmente '
                        f'(convergencia {info["order"]["label"]}).')
    elif lam > 1 + 1e-9:
        info['verdict'] = 'diverge'
        info['text'] = (f'|φ′| = {lam:.4g} > 1 {where}: x* repele las aproximaciones; '
                        'solo converge si x₀ cae exactamente en x*.')
    else:
        info['text'] = '|φ′| = 1: el criterio no decide; la convergencia, si ocurre, sería sublineal.'
    return info


def _analyze_bracket(method, f, cleaned):
    a, b = cleaned['a'], cleaned['b']
    fa, fb = _safe(f, a), _safe(f, b)
    ok = fa is not None and fb is not None and fa * fb < 0
    detail = (f'f({a:g}) = {fa:.4g} y f({b:g}) = {fb:.4g}: signos opuestos.' if ok
              else 'f(a) y f(b) no tienen signos opuestos: no hay garantía de raíz en [a, b].'
              if fa is not None and fb is not None else 'No se pudo evaluar f en los extremos.')
    bound = (r'|x_n-x^{*}|\le \frac{b-a}{2^{n}}' if method == 'bisection'
             else r'x_r=a-\frac{f(a)(b-a)}{f(b)-f(a)}\ \text{(convergencia lineal)}')
    return {'kind': 'bracket', 'verdict': 'converge' if ok else 'inconclusive',
            'criterion_tex': r'f(a)\,f(b)<0', 'formula_tex': bound, 'dphi_tex': None, 'lambda': None,
            'lambda_at': None, 'curve': None, 'iterates': [],
            'order': {'p': 1, 'label': 'lineal, factor 1/2' if method == 'bisection' else 'lineal'},
            'text': ('Converge siempre que f sea continua y f(a)·f(b) < 0 (teorema del valor intermedio).'
                     if ok else 'Sin cambio de signo no se garantiza convergencia.'),
            'checks': [_check(ok, 'Cambio de signo f(a)·f(b) < 0', detail)]}


def _analyze_secant(f, root, iterates, cleaned):
    slope = _safe(f.derivative(), root) if root is not None else None
    second = _safe(f.derivative(2), root) if root is not None else None
    simple = slope is not None and abs(slope) > 1e-6
    constant = abs(second / (2 * slope)) if simple and second is not None else None
    checks = [_derivative_check(f.expression, 1, [x for x in (iterates[:1] + [root]) if x is not None],
                                'Derivada f′(x) (solo para verificar el criterio)')]
    checks.append(_check(simple if slope is not None else None, 'Raíz simple (f′(x*) ≠ 0)',
                         'f′(x*) ≈ 0: raíz múltiple; la secante pierde orden.' if slope is not None and not simple
                         else 'f′(x*) no nula.' if simple else 'No se pudo evaluar f′(x*).'))
    return {'kind': 'secant', 'verdict': 'converge' if simple else 'inconclusive',
            'criterion_tex': r"f'(x^{*})\neq 0,\quad e_{n+1}\approx C\,e_n\,e_{n-1}",
            'formula_tex': r"C=\left|\frac{f''(x^{*})}{2f'(x^{*})}\right|,\quad p=\frac{1+\sqrt5}{2}\approx1.618",
            'dphi_tex': None, 'lambda': constant, 'lambda_at': 'C', 'curve': None, 'iterates': [],
            'order': {'p': GOLDEN, 'label': 'superlineal, p ≈ 1.618'} if simple else {'p': 1, 'label': 'lineal'},
            'text': (f'Converge localmente con orden ≈ 1.618 (C = {constant:.4g}).' if simple and constant is not None
                     else 'Converge localmente con orden ≈ 1.618.' if simple
                     else 'Sin f′(x*) ≠ 0 no se garantiza el orden superlineal.'),
            'checks': checks}
