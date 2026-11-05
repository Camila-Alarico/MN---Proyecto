from .parser import parse_function, finite, MathInputError
from .common import controls, result, near_zero, num


def substituted_formula(method, a, b, fa, fb, x):
    """Fórmula del paso con los valores numéricos sustituidos (texto plano)."""
    if method == 'bisection':
        return f'xₘ = (a + b)/2 = ({num(a)} + {num(b)})/2 = {num(x, 8)}'
    return (f'xᵣ = a − f(a)(b − a)/(f(b) − f(a)) = {num(a)} − {num(fa)}·({num(b)} − {num(a)})'
            f'/({num(fb)} − {num(fa)}) = {num(x, 8)}')


def solve_bracket(method, expression, a, b, tolerance=0.0001, max_iterations=100):
    tol, count = controls(tolerance, max_iterations)
    f = parse_function(expression)
    a, b = finite(a, 'a'), finite(b, 'b')
    if a >= b:
        raise MathInputError('El extremo a debe ser menor que b.')
    fa, fb = f(a), f(b)
    for x, fx in [(a, fa), (b, fb)]:
        if fx == 0:
            return result(method, x, [], True, 'Un extremo tiene residuo cero en la precisión disponible.', residual=0.0)
    if (fa > 0) == (fb > 0):
        raise MathInputError('No existe garantía de una raíz en este intervalo porque f(a) y f(b) tienen el mismo signo.')
    # Sampling catches common domain holes, but cannot prove continuity.
    for i in range(1, 17):
        f(a + (b - a) * i / 17)
    rows, previous = [], None
    for n in range(1, count + 1):
        if method == 'false-position' and near_zero(fb - fa, max(abs(fa), abs(fb))):
            return result(method, previous, rows, False, 'Denominador demasiado pequeño; método inestable.')
        x = (a + b) / 2 if method == 'bisection' else a - fa * (b - a) / (fb - fa)
        fx = f(x)
        error = abs(x - previous) if previous is not None else None
        if fx == 0:
            new_a, new_b, message = x, x, 'Encontramos una raíz exacta en la precisión disponible.'
        elif (fa > 0) != (fx > 0):
            new_a, new_b = a, x
            message = 'Como f(a) y f(Xm) tienen signos diferentes, la raíz permanece en [a, Xm].'
        else:
            new_a, new_b = x, b
            message = 'Como f(Xm) y f(b) tienen signos diferentes, la raíz permanece en [Xm, b].'
        bound = (b - a) / 2 if method == 'bisection' else None
        rows.append({'n': n, 'a': a, 'b': b, 'x': x, 'fa': fa, 'fb': fb, 'fx': fx,
                     'error': error, 'error_bound': bound, 'new_a': new_a, 'new_b': new_b,
                     'formula': substituted_formula(method, a, b, fa, fb, x),
                     'explanation': message.replace('Xm', 'xr') if method == 'false-position' else message})
        # Small residual alone is scale dependent. Require a step or interval bound too.
        converged = fx == 0 or (method == 'bisection' and bound <= tol and abs(fx) <= tol) or (
            error is not None and error <= tol and abs(fx) <= tol)
        if converged:
            reason = ('Residuo cero en la precisión disponible.' if fx == 0 else
                      'Cota de intervalo y residuo dentro de la tolerancia.' if method == 'bisection' else
                      'Paso absoluto y residuo dentro de la tolerancia.')
            return result(method, x, rows, True, reason + ' Se supone continuidad en el intervalo.')
        if x == a or x == b:
            return result(method, x, rows, False, 'Estancamiento de precisión sin satisfacer el residuo.')
        a, b = new_a, new_b
        fa, fb = f(a), f(b)
        previous = x
    return result(method, x, rows, False, 'Se alcanzó el máximo de iteraciones sin satisfacer el criterio.')
