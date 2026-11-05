"""Constantes y utilidades comunes de los métodos para sistemas lineales (módulo 2)."""
from nonlinear.services.common import num  # número breve para fórmulas sustituidas

# Criterio declarado de pivote problemático: |pivote| < ε·max|aᵢⱼ| (máximo sobre la matriz A original).
PIVOT_EPS = 1e-12        # por debajo: sistema singular o casi singular, se detiene
SMALL_PIVOT_EPS = 1e-6   # por debajo: se avisa de pivote pequeño y se continúa
DIVERGENCE_LIMIT = 1e12  # Gauss-Seidel se detiene si alguna componente supera este valor

CRITERION = (
    f'Un pivote es problemático si |pivote| < ε·max|aᵢⱼ|, con el máximo tomado sobre la matriz A original. '
    f'Con ε = {PIVOT_EPS:g} el sistema se declara singular (o casi singular) y no se calcula solución; '
    f'con ε = {SMALL_PIVOT_EPS:g} se avisa de un pivote pequeño y se continúa.'
)


def matrix_scale(matrix):
    return max(abs(value) for row in matrix for value in row)


def is_negligible(value, scale, eps=PIVOT_EPS):
    """|valor| < ε·escala; una matriz nula (escala 0) siempre es singular."""
    return scale == 0 or abs(value) < eps * scale


def residual_vector(matrix, vector, x):
    """r = b − A·x."""
    return [vector[i] - sum(a * xj for a, xj in zip(row, x)) for i, row in enumerate(matrix)]


def residual_inf(matrix, vector, x):
    return max(abs(r) for r in residual_vector(matrix, vector, x))


def dominance(matrix):
    """Dominancia diagonal estricta por filas: |aᵢᵢ| > Σ_{j≠i} |aᵢⱼ|."""
    rows = []
    for i, row in enumerate(matrix):
        off = sum(abs(v) for j, v in enumerate(row) if j != i)
        rows.append({'row': i + 1, 'diagonal': abs(row[i]), 'off_diagonal': off, 'strict': abs(row[i]) > off})
    return {'strict': all(r['strict'] for r in rows), 'rows': rows}
