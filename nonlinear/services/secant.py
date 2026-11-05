from .open_methods import solve_open


def solve_secant(expression, x0, x1, tolerance=0.0001, max_iterations=100):
    return solve_open('secant', expression, x0, tolerance, max_iterations, x1=x1)
