from .open_methods import solve_open


def solve_multiple_roots(expression, x0, tolerance=0.0001, max_iterations=100):
    return solve_open('multiple-roots', expression, x0, tolerance, max_iterations)
