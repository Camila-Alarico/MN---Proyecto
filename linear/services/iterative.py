"""Gauss-Seidel desde el vector cero."""
import math

from .common import DIVERGENCE_LIMIT, dominance, is_negligible, matrix_scale, residual_inf, residual_vector


def gauss_seidel(matrix, vector, tolerance, max_iterations):
    n = len(matrix)
    x = [0.0] * n
    rows = [{'n': 0, 'x': x[:], 'step': None, 'residual': residual_inf(matrix, vector, x)}]
    info = dominance(matrix)
    if info['strict']:
        note = ('La matriz tiene dominancia diagonal estricta por filas: esto es una condición suficiente '
                '(no necesaria) para que Gauss-Seidel converja desde cualquier vector inicial.')
    else:
        note = ('La matriz no tiene dominancia diagonal estricta. Como esa condición es solo suficiente, '
                'la convergencia no queda garantizada por este criterio, pero tampoco se descarta: se comprueba iterando.')
    answer = {'success': True, 'method': 'seidel', 'dominance': info, 'convergence_note': note,
              'tolerance': tolerance, 'max_iterations': max_iterations, 'iterations': rows}

    scale = matrix_scale(matrix)
    if any(is_negligible(matrix[i][i], scale) for i in range(n)):
        return {**answer, 'solution': None, 'residual': None, 'residual_vector': None, 'converged': False,
                'iterations_count': 0, 'status': 'Diagonal nula',
                'message': 'Hay un elemento diagonal nulo (o casi): Gauss-Seidel divide entre aᵢᵢ. Reordena las filas.'}

    status, message = 'No convergió', f'No se alcanzó la tolerancia en {max_iterations} iteraciones.'
    for k in range(1, max_iterations + 1):
        old = x[:]
        for i in range(n):
            s = sum(matrix[i][j] * x[j] for j in range(n) if j != i)
            x[i] = (vector[i] - s) / matrix[i][i]
        if not all(math.isfinite(v) and abs(v) < DIVERGENCE_LIMIT for v in x):
            status, message = 'Diverge', 'Las componentes crecen sin control: Gauss-Seidel diverge con este sistema y orden de filas.'
            x = old
            break
        step = max(abs(a - b) for a, b in zip(x, old))
        res = residual_inf(matrix, vector, x)
        rows.append({'n': k, 'x': x[:], 'step': step, 'residual': res})
        if step <= tolerance and res <= tolerance:
            status, message = 'Convergió', 'Paso y residuo (norma infinita) dentro de la tolerancia.'
            break
    converged = status == 'Convergió'
    r = residual_vector(matrix, vector, x)
    return {**answer, 'solution': x if converged else None, 'last_iterate': x,
            'residual_vector': r, 'residual': max(abs(v) for v in r), 'converged': converged,
            'iterations_count': len(rows) - 1, 'status': status, 'message': message}
