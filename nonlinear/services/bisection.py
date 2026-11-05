from .bracketing import solve_bracket


def solve_bisection(expression, a, b, tolerance=0.0001, max_iterations=100):
    return solve_bracket('bisection', expression, a, b, tolerance, max_iterations)
