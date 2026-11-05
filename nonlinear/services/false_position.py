from .bracketing import solve_bracket


def solve_false_position(expression, a, b, tolerance=0.0001, max_iterations=100):
    return solve_bracket('false-position', expression, a, b, tolerance, max_iterations)
