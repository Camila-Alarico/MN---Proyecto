from .parser import parse_function, finite, MathInputError


def sample_function(expression, a=-2, b=3, samples=161):
    f = parse_function(expression)
    a, b = finite(a), finite(b)
    if a >= b:
        raise MathInputError('El límite izquierdo debe ser menor que el derecho.')
    xs, ys, intervals, sampled_zeros = [], [], [], []
    for i in range(samples):
        x = a + (b - a) * i / (samples - 1)
        try:
            y = f(x)
        except MathInputError:
            y = None
        if y == 0:
            sampled_zeros.append(x)
        # A zero endpoint is a separate observation, not a strict sign change.
        # Compare signs without multiplying: tiny values could underflow.
        if ys and y is not None and ys[-1] is not None and y != 0 and ys[-1] != 0 and (y > 0) != (ys[-1] > 0):
            intervals.append([xs[-1], x])
        xs.append(x)
        ys.append(y)
    return {'x': xs, 'y': ys, 'intervals': intervals, 'sampled_zeros': sampled_zeros, 'formula': f.latex,
            'warning': 'Un cambio de signo sugiere una raíz solo si la función es continua. El muestreo puede omitir raíces múltiples o discontinuidades.'}
