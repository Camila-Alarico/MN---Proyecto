from time import perf_counter
from .bisection import solve_bisection
from .false_position import solve_false_position
from .fixed_point import solve_fixed_point
from .newton import solve_newton
from .secant import solve_secant
from .multiple_roots import solve_multiple_roots
from .plotting import sample_function
from ..catalog import METHODS

SOLVERS = {'bisection': solve_bisection, 'false-position': solve_false_position,
           'fixed-point': solve_fixed_point, 'newton': solve_newton,
           'secant': solve_secant, 'multiple-roots': solve_multiple_roots}


def focus_range(plot, lo, hi):
    """Rango vertical sugerido para que el intervalo/puntos del método llenen la vista.

    Plotly autoajusta Y a toda la muestra (por ejemplo hasta f(3)=22 para x³−x−2 en [1,2]),
    lo que aplasta la zona de interés. Aquí se toma el rango de f solo alrededor de
    [lo, hi], incluyendo siempre y=0 para que la raíz quede visible.
    """
    pad = max((hi - lo) * 0.15, 0.35)
    ys = [y for x, y in zip(plot['x'], plot['y']) if y is not None and lo - pad <= x <= hi + pad]
    if len(ys) < 2:
        return None
    low, high = min(ys + [0.0]), max(ys + [0.0])
    margin = max((high - low) * 0.12, 1e-9)
    return [low - margin, high + margin]


def calculate(method, data, with_plot=True):
    params = {key: data[key] for key in ['expression', 'tolerance', 'max_iterations'] + METHODS[method]['parameters']}
    start = perf_counter()
    answer = SOLVERS[method](**params)
    answer['elapsed_ms'] = (perf_counter() - start) * 1000
    if not with_plot:  # el comparador no dibuja la gráfica de cada método
        return answer
    # Keep the graph focused on the initial region, even if an iteration diverges.
    points = [params[k] for k in METHODS[method]['parameters']]
    if answer['root'] is not None and abs(answer['root']) < 100:
        points.append(answer['root'])
    lo, hi = min(points), max(points)
    pad = max((hi - lo) * 0.4, 1)
    answer['plot'] = sample_function(params['expression'], max(-1e12, lo - pad), min(1e12, hi + pad))
    answer['plot']['y_range'] = focus_range(answer['plot'], lo, hi)
    return answer
