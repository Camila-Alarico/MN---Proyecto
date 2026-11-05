"""Eliminación gaussiana con pivoteo parcial y sustitución hacia atrás."""
import math

from nonlinear.services.parser import MathInputError

from .common import (CRITERION, PIVOT_EPS, SMALL_PIVOT_EPS, is_negligible, matrix_scale, num, residual_inf,
                     residual_vector)


def gauss_pivot(matrix, vector):
    n = len(matrix)
    scale = matrix_scale(matrix)
    aug = [list(row) + [vector[i]] for i, row in enumerate(matrix)]
    steps, warnings = [], []
    base = {'success': True, 'method': 'gauss', 'criterion': CRITERION, 'scale': scale,
            'augmented': [r[:] for r in aug], 'steps': steps, 'warnings': warnings}

    for k in range(n):
        p = max(range(k, n), key=lambda i: abs(aug[i][k]))  # en empates conserva la fila más alta
        pivot = aug[p][k]
        if is_negligible(pivot, scale):
            warnings.append(
                f'Columna {k + 1}: el mejor pivote disponible es {num(pivot)} y |pivote| < ε·max|aᵢⱼ| '
                f'(ε = {PIVOT_EPS:g}, max|aᵢⱼ| = {num(scale)}). El sistema es singular o casi singular.')
            return {**base, 'singular': True, 'solution': None, 'residual': None, 'residual_vector': None,
                    'converged': False, 'status': 'Sistema singular', 'iterations_count': len(steps),
                    'swaps': sum(1 for s in steps if s['swap']),
                    'message': 'No existe solución única: el sistema es singular o casi singular. '
                               'No se calculó ninguna solución (evitamos dividir entre un pivote nulo).'}
        step = {'column': k + 1, 'pivot': pivot, 'pivot_row': p + 1, 'swap': None, 'small_pivot': False}
        if abs(pivot) < SMALL_PIVOT_EPS * scale:
            step['small_pivot'] = True
            warnings.append(f'Columna {k + 1}: pivote pequeño ({num(pivot)} < {SMALL_PIVOT_EPS:g}·{num(scale)}). '
                            'La solución puede perder cifras significativas.')
        if p != k:
            aug[k], aug[p] = aug[p], aug[k]
            step['swap'] = {'from': k + 1, 'to': p + 1}
        step['after_swap'] = [r[:] for r in aug]
        multipliers = []
        for i in range(k + 1, n):
            m = aug[i][k] / pivot
            multipliers.append({'row': i + 1, 'value': m})
            for j in range(k, n + 1):
                aug[i][j] -= m * aug[k][j]
            aug[i][k] = 0.0
        step['multipliers'] = multipliers
        step['after'] = [r[:] for r in aug]
        steps.append(step)

    x, back = [0.0] * n, []
    for i in reversed(range(n)):
        tail = sum(aug[i][j] * x[j] for j in range(i + 1, n))
        x[i] = (aug[i][n] - tail) / aug[i][i]
        terms = ''.join(f' − {num(aug[i][j])}·{num(x[j])}' for j in range(i + 1, n))
        back.append({'row': i + 1, 'value': x[i],
                     'formula': f'x{i + 1} = ({num(aug[i][n])}{terms}) / {num(aug[i][i])}'})
    if not all(math.isfinite(v) for v in x):
        raise MathInputError('Los valores del sistema producen una solución fuera del rango numérico.')
    r = residual_vector(matrix, vector, x)
    return {**base, 'singular': False, 'solution': x, 'upper': [row[:] for row in aug], 'back_substitution': back,
            'residual_vector': r, 'residual': max(abs(v) for v in r), 'converged': True, 'status': 'Resuelto',
            'iterations_count': len(steps), 'swaps': sum(1 for s in steps if s['swap']),
            'message': 'Solución obtenida por eliminación gaussiana con pivoteo parcial.'}
