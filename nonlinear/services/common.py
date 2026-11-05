from .parser import MathInputError, finite


def controls(tolerance, max_iterations):
    tolerance = finite(tolerance, 'Tolerancia')
    count = finite(max_iterations, 'Iteraciones')
    if not 1e-12 <= tolerance <= 0.1:
        raise MathInputError('La tolerancia debe estar entre 10⁻¹² y 0.1.')
    if count != int(count) or not 1 <= count <= 200:
        raise MathInputError('El máximo de iteraciones debe ser un entero entre 1 y 200.')
    return tolerance, int(count)


def result(method, root, rows, converged, message, **extra):
    return {'success': True, 'method': method, 'root': root,
            'iterations_count': len(rows), 'converged': converged,
            # `error` is retained for API/history compatibility; it is a step, not root error.
            'iterations': rows, 'error': rows[-1]['error'] if rows else None,
            'residual': abs(rows[-1]['fx']) if rows else None,
            'status': 'Convergió' if converged else 'No convergió', 'message': message, **extra}


def near_zero(denominator, scale=1):
    return abs(denominator) <= 1e-14 * max(abs(scale), 1e-300)


def num(value, digits=6):
    """Número breve para fórmulas sustituidas; los negativos van entre paréntesis."""
    text = f'{value:.{digits}g}'
    if 'e' in text:
        mantissa, exponent = text.split('e')
        text = f'{mantissa}×10^{int(exponent)}'
    return f'({text})' if value < 0 else text
