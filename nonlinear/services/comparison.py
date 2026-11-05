"""Comparador de recorridos: iteraciones, error y propagación del error entre métodos.

Un *recorrido* es una ejecución completa de un método (conceptos.html: «una ecuación, dos
recorridos»): la sucesión x₀, x₁, x₂, … hasta cumplir el criterio de parada. Para comparar recorridos
con una vara común se fija una raíz de referencia x* (refinada con mpmath a 50 cifras) y se usan las
definiciones de errores.html mediante `calculate_errors`:

    Eₐ = |x* − x̃|,   Eᵣ = Eₐ / |x*|,   Eₚ = 100·Eᵣ,   aceptado si Eₐ ≤ τ.

Propagación del error, en tres sentidos:
  1. Entre iteraciones: factor Eₙ₊₁/Eₙ y orden observado p ≈ ln(Eₙ₊₁/Eₙ)/ln(Eₙ/Eₙ₋₁); constante
     asintótica λ ≈ Eₙ₊₁/Eₙᵖ.
  2. Entre métodos: |xA − xB| ≤ Eₐ(A) + Eₐ(B) (desigualdad triangular). Si se viola, alguna
     aproximación no es tan buena como dice su residuo o la referencia es dudosa.
  3. Del residuo a la raíz: f(x) ≈ f′(x*)(x − x*), luego Eₐ ≈ |f(x)|/|f′(x*)|. El número de
     condición de la raíz κ = 1/|f′(x*)| indica cuánto amplifica una tolerancia de residuo.
"""
import math
from time import perf_counter

import mpmath as mp
import sympy as sp

from ..catalog import METHODS
from .common import controls
from .convergence import GOLDEN, analyze
from .errors import calculate_errors
from .parser import X, MathInputError, parse_function
from .solving import run_method

ERROR_FLOOR = 1e-14  # por debajo, el ruido de redondeo domina las razones entre errores
THEORY = {
    'bisection': (1.0, 'lineal (factor 1/2)'), 'false-position': (1.0, 'lineal'),
    'fixed-point': (1.0, 'lineal si |g′(x*)| > 0'), 'newton': (2.0, 'cuadrática (raíz simple)'),
    'secant': (GOLDEN, 'superlineal, p ≈ 1.618'), 'multiple-roots': (2.0, 'cuadrática con f y f′ y f″'),
}


def _num(value):
    """float finito o None: el JSON de la API no admite NaN ni infinitos."""
    if value is None or isinstance(value, bool):
        return None
    try:
        value = float(value)
    except (TypeError, ValueError):
        return None
    return value if math.isfinite(value) else None


def _clean(obj):
    if isinstance(obj, dict):
        return {key: _clean(value) for key, value in obj.items()}
    if isinstance(obj, (list, tuple)):
        return [_clean(value) for value in obj]
    if isinstance(obj, float):
        return _num(obj)
    return obj


def _at(function, x):
    try:
        return function(x)
    except MathInputError:
        return None


def refine_root(f, start, tol):
    """Raíz de f cerca de `start` con 50 cifras, o None si no se puede validar.

    Se resuelve u = f/f′, que tiene la misma raíz que f pero siempre simple: así también sirve
    para raíces múltiples, donde Newton y la secante sobre f perderían precisión.
    """
    expression = f.expression
    try:
        with mp.workdps(50):
            value = sp.lambdify(X, expression, 'mpmath')
            slope = sp.lambdify(X, sp.diff(expression, X), 'mpmath')
            root = mp.findroot(lambda t: value(t) / slope(t), mp.mpf(start), tol=mp.mpf(10) ** -40, maxsteps=80)
            root = float(root)
    except (ZeroDivisionError, ValueError, TypeError, OverflowError, mp.libmp.NoConvergence):
        return None
    limit = max(1e-2 * (1 + abs(start)), 100 * tol)
    return root if math.isfinite(root) and abs(root - start) <= limit else None


def _reference(f, results, tol):
    """(raíz, origen, precisa) a partir de las mejores aproximaciones disponibles."""
    scored = []
    for entry in results.values():
        root = entry['answer'].get('root') if entry.get('answer') else None
        residual = _at(f, root) if root is not None else None
        if residual is not None:
            scored.append((not entry['answer']['converged'], abs(residual), root))
    if not scored:
        return None, 'sin referencia', False
    _, _, start = min(scored)
    refined = refine_root(f, start, tol)
    if refined is not None:
        return refined, 'mpmath (50 cifras)', True
    return start, 'mejor aproximación de los métodos', False


def _path(method, answer):
    """Aproximaciones del recorrido: [(n, x, paso)]. Los métodos abiertos incluyen x₀ como n = 0."""
    rows = answer.get('iterations') or []
    path = [(0, rows[0]['xn'], None)] if rows and method in ('fixed-point', 'newton', 'secant', 'multiple-roots') else []
    path += [(row['n'], row['x'], row['error']) for row in rows]
    if not path and answer.get('root') is not None:
        path = [(0, answer['root'], None)]  # raíz exacta en un extremo o en x₀
    return path


def _error_rows(path, f, ref, bounds):
    rows, previous, before = [], None, None
    for n, x, step in path:
        errors = None
        if ref is not None:
            try:
                errors = calculate_errors(ref, x)
            except MathInputError:
                errors = None  # iterado fuera de ±10¹²: el recorrido diverge
        absolute = errors['absolute'] if errors else None
        residual = _at(f, x)
        ratio = order = None
        if absolute is not None and previous and previous > ERROR_FLOOR and absolute > 0:
            ratio = absolute / previous
            if before and before > ERROR_FLOOR and previous != before and absolute > ERROR_FLOOR:
                denominator = math.log(previous / before)
                if abs(denominator) > 1e-9:
                    estimate = math.log(absolute / previous) / denominator
                    order = estimate if 0 < estimate < 10 else None
        rows.append({'n': n, 'x': x, 'step': step, 'residual': None if residual is None else abs(residual),
                     'absolute': absolute, 'relative': errors['relative'] if errors else None,
                     'percentage': errors['percentage'] if errors else None, 'ratio': ratio,
                     'order': order, 'bound': bounds.get(n)})
        before, previous = previous, absolute
    return rows


def _first(rows, key, tol):
    return next((row['n'] for row in rows if row[key] is not None and row[key] <= tol), None)


def _summary(method, rows, ref_slope, tol):
    p_theory, label = THEORY[method]
    if method == 'newton' and ref_slope is not None and abs(ref_slope) < 1e-6:
        p_theory, label = 1.0, 'lineal (raíz múltiple)'
    observed = [row['order'] for row in rows if row['order'] is not None][-3:]
    observed.sort()
    order = observed[len(observed) // 2] if observed else None
    constant = None
    if len(rows) >= 2 and rows[-2]['absolute'] and rows[-1]['absolute'] is not None and rows[-2]['absolute'] > ERROR_FLOOR:
        constant = rows[-1]['absolute'] / rows[-2]['absolute'] ** p_theory
    return {'theoretical_order': p_theory, 'theoretical_label': label, 'observed_order': order,
            'asymptotic_constant': constant,
            'iterations_to_tolerance': {'error': _first(rows, 'absolute', tol), 'step': _first(rows, 'step', tol),
                                        'residual': _first(rows, 'residual', tol)}}


def _validate_request(data):
    keys = data.get('methods')
    if not isinstance(keys, list) or not keys or len(keys) > len(METHODS):
        raise MathInputError('Selecciona al menos un método para comparar.')
    seen = []
    for key in keys:
        if key not in METHODS:
            raise MathInputError('Método desconocido.')
        if key not in seen:
            seen.append(key)
    tol, count = controls(data.get('tolerance'), data.get('max_iterations'))
    return seen, tol, count


def compare_methods(data):
    keys, tol, count = _validate_request(data)
    expression = data.get('expression')
    f = parse_function(expression)
    base = {k: data[k] for k in ('a', 'b', 'x0', 'x1') if data.get(k) not in (None, '')}
    base.update(tolerance=tol, max_iterations=count)

    results = {}
    for key in keys:
        payload = {**base, 'expression': expression}
        if key == 'fixed-point':
            if not data.get('g'):
                results[key] = {'error': 'Escribe g(x), la transformación equivalente a f(x)=0.'}
                continue
            payload.update(expression=data['g'], reference_expression=expression)
        try:
            cleaned, answer = run_method(key, payload, with_plot=False)
            results[key] = {'answer': answer, 'cleaned': cleaned}
        except MathInputError as exc:
            results[key] = {'error': str(exc)}

    ref, origin, precise = _reference(f, {k: v for k, v in results.items() if 'answer' in v}, tol)
    slope = _at(f.derivative(), ref) if ref is not None else None
    dfr = None if slope is None else abs(slope)

    methods = []
    for key in keys:
        entry, title = results[key], METHODS[key]['title']
        if 'answer' not in entry:
            methods.append({'key': key, 'title': title, 'converged': False, 'root': None, 'message': entry['error'],
                            'iterations_count': 0, 'rows': [], 'convergence': None})
            continue
        answer, cleaned = entry['answer'], entry['cleaned']
        path = _path(key, answer)
        bounds = {row['n']: row['error_bound'] for row in answer.get('iterations', []) if row.get('error_bound') is not None}
        rows = _error_rows(path, f, ref, bounds)
        iter_f = parse_function(data['g']) if key == 'fixed-point' else f
        try:
            convergence = analyze(key, iter_f, f, ref, [x for _, x, _ in path], cleaned, tol, precise)
        except MathInputError as exc:
            convergence = {'kind': 'unavailable', 'verdict': 'inconclusive', 'text': str(exc), 'checks': []}
        last = rows[-1] if rows else {}
        final_residual = last.get('residual')
        methods.append({
            'key': key, 'title': title, 'converged': answer['converged'], 'status': answer['status'],
            'message': answer['message'], 'root': answer['root'], 'iterations_count': answer['iterations_count'],
            'elapsed_ms': answer.get('elapsed_ms'), 'rows': rows, 'summary': _summary(key, rows, slope, tol),
            'final': {'absolute': last.get('absolute'), 'relative': last.get('relative'),
                      'percentage': last.get('percentage'), 'residual': final_residual,
                      'accepted': last.get('absolute') is not None and last['absolute'] <= tol,
                      # Eₐ ≈ |f(x)|/|f′(x*)|: cuánto error de la raíz explica el residuo final
                      'error_from_residual': None if not dfr or final_residual is None else final_residual / dfr},
            'convergence': convergence,
        })

    return _clean({'success': True, 'tolerance': tol, 'max_iterations': count, 'reference': {
        'root': ref, 'source': origin, 'precise': precise, 'derivative': slope,
        'condition_number': None if not dfr else 1 / dfr,
        'root_error_from_tolerance': None if not dfr else tol / dfr,
        'multiple_root': dfr is not None and dfr < 1e-6},
        'methods': methods, 'propagation': _propagation(methods), 'ranking': _ranking(methods)})


def _propagation(methods):
    """Discrepancia entre pares de métodos frente a la cota Eₐ(A) + Eₐ(B)."""
    usable = [m for m in methods if m.get('root') is not None and m.get('final', {}).get('absolute') is not None]
    pairs = []
    for i, first in enumerate(usable):
        for second in usable[i + 1:]:
            gap = abs(first['root'] - second['root'])
            bound = first['final']['absolute'] + second['final']['absolute']
            scale = max(abs(first['root']), abs(second['root']))
            pairs.append({'a': first['title'], 'b': second['title'], 'difference': gap, 'bound': bound,
                          'relative': gap / scale if scale else None,
                          'consistent': gap <= bound * (1 + 1e-9) + 1e-15})
    return pairs


def _ranking(methods):
    scored = [m for m in methods if m.get('final', {}).get('absolute') is not None and m['converged']]
    if not scored:
        return {'fewest_iterations': None, 'most_accurate': None, 'ratios': {}}
    best = min(scored, key=lambda m: m['final']['absolute'])
    fastest = min((m for m in scored if m['summary']['iterations_to_tolerance']['error'] is not None),
                  key=lambda m: m['summary']['iterations_to_tolerance']['error'], default=None)
    floor = max(best['final']['absolute'], 1e-300)
    return {'most_accurate': best['title'], 'fewest_iterations': fastest['title'] if fastest else None,
            'ratios': {m['title']: m['final']['absolute'] / floor for m in scored}}
