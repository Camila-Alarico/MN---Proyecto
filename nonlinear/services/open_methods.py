from .parser import parse_function, finite, MathInputError
from .common import controls, result, near_zero, num


def solve_open(method, expression, x0, tolerance=0.0001, max_iterations=100, x1=None):
    tol, count = controls(tolerance, max_iterations)
    f = parse_function(expression)
    x = finite(x0, 'x0')
    df = f.derivative() if method in ('newton', 'multiple-roots') else None
    ddf = f.derivative(2) if method == 'multiple-roots' else None
    meta = {'derivative': df.latex if df else None, 'second_derivative': ddf.latex if ddf else None}
    if method == 'fixed-point':
        try:
            meta['local_slope'] = abs(f.derivative()(x))
        except MathInputError:
            meta['local_slope'] = None
    previous = finite(x1, 'x1') if method == 'secant' else None
    if method == 'secant':
        previous, x = x, previous
    rows = []
    for n in range(1, count + 1):
        residual = None
        try:
            fx = f(x)
            residual = fx - x if method == 'fixed-point' else fx
            if residual == 0:
                return result(method, x, rows, True, 'Residuo cero en la precisión disponible.', residual=0.0, **meta)
            row = {'n': n, 'xn': x, 'fxn': fx}
            if method == 'fixed-point':
                next_x = fx
                message = 'Evaluamos g(xn); la escalera alterna entre y = g(x) e y = x.'
                formula = f'xₙ₊₁ = g(xₙ) = g({num(x)}) = {num(next_x, 8)}'
            elif method == 'secant':
                fp = f(previous)
                denominator = fx - fp
                if near_zero(denominator, max(abs(fx), abs(fp))):
                    raise MathInputError('Las imágenes son iguales o demasiado cercanas: denominador de secante casi cero.')
                next_x = x - fx * (x - previous) / denominator
                row.update({'previous': previous, 'fprevious': fp})
                message = 'La recta secante por las dos aproximaciones corta el eje X en la siguiente aproximación.'
                formula = (f'xₙ₊₁ = xₙ − f(xₙ)(xₙ − xₙ₋₁)/(f(xₙ) − f(xₙ₋₁)) = {num(x)} − {num(fx)}·({num(x)} − {num(previous)})'
                           f'/({num(fx)} − {num(fp)}) = {num(next_x, 8)}')
            else:
                slope = df(x)
                row['dfx'] = slope
                if method == 'newton':
                    # Scale-invariant guard: rescaling f must not change the Newton step.
                    if near_zero(slope, abs(fx) / max(1, abs(x))):
                        raise MathInputError('La derivada es nula o demasiado pequeña respecto a f(x); el paso sería excesivo. Cambia el punto inicial.')
                    next_x = x - fx / slope
                    formula = f'xₙ₊₁ = xₙ − f(xₙ)/f′(xₙ) = {num(x)} − {num(fx)}/{num(slope)} = {num(next_x, 8)}'
                else:
                    second = ddf(x)
                    denominator = slope * slope - fx * second
                    row['ddfx'] = second
                    if near_zero(denominator, max(slope * slope, abs(fx * second))):
                        raise MathInputError('El denominador de Newton modificado es casi cero.')
                    next_x = x - fx * slope / denominator
                    formula = (f'xₙ₊₁ = xₙ − f·f′/(f′² − f·f″) = {num(x)} − {num(fx)}·{num(slope)}'
                               f'/({num(slope)}² − {num(fx)}·{num(second)}) = {num(next_x, 8)}')
                message = (f'Construimos la tangente en x = {x:.8g}. Su intersección con el eje X produce la siguiente aproximación.'
                           if method == 'newton' else 'Combinamos f, f′ y f″ para corregir el efecto de una raíz múltiple.')
            next_x = finite(next_x, 'Nueva aproximación (posible divergencia)')
            next_value = f(next_x)
            next_residual = next_value - next_x if method == 'fixed-point' else next_value
            error = abs(next_x - x)
            row.update({'x': next_x, 'fx': next_residual, 'error': error, 'explanation': message, 'formula': formula})
            rows.append(row)
            if next_residual == 0 or (error <= tol and abs(next_residual) <= tol):
                message = ('Residuo cero en la precisión disponible.' if next_residual == 0 else
                           'Paso absoluto y residuo dentro de la tolerancia. El paso no es una cota del error real.')
                return result(method, next_x, rows, True, message, **meta)
            if len(rows) >= 3 and abs(next_x - rows[-3]['x']) <= 1e-14 * max(1, abs(next_x)) and error > tol:
                return result(method, next_x, rows, False, 'Oscilación probable: se repiten aproximaciones sin converger.', **meta)
            if next_x == x:
                return result(method, next_x, rows, False, 'Estancamiento sin satisfacer el residuo.', **meta)
            previous, x = x, next_x
        except MathInputError as exc:
            return result(method, x, rows, False, str(exc),
                          residual=abs(residual) if residual is not None else None, **meta)
    return result(method, x, rows, False, 'Máximo de iteraciones alcanzado; revisa convergencia y puntos iniciales.', **meta)
