"""Ejemplo educativo. Ejecutar con Python 3: python3 biseccion.py."""
import math


def biseccion(f, a, b, tolerancia=1e-6, max_iteraciones=100):
    """Requiere f continua en [a, b]; devuelve aproximación y cota absoluta."""
    if not (math.isfinite(a) and math.isfinite(b) and a < b):
        raise ValueError('Usa extremos finitos con a < b.')
    if not math.isfinite(tolerancia) or tolerancia <= 0 or max_iteraciones < 1:
        raise ValueError('Usa tolerancia e iteraciones positivas.')
    fa, fb = f(a), f(b)
    if not (math.isfinite(fa) and math.isfinite(fb)):
        raise ValueError('La función debe ser finita en los extremos.')
    if fa == 0:
        return a, 0
    if fb == 0:
        return b, 0
    if (fa > 0) == (fb > 0):
        raise ValueError('Se necesita cambio de signo en los extremos.')
    print('Iteración | Punto medio | Cota de error | Residuo')
    for n in range(1, max_iteraciones + 1):
        medio = a + (b - a) / 2
        fm, cota = f(medio), (b - a) / 2
        if not math.isfinite(fm):
            raise ValueError('La función no es finita dentro del intervalo.')
        print(f'{n:9d} | {medio:.9f} | {cota:.9g} | {abs(fm):.9g}')
        if fm == 0:
            return medio, 0
        if cota <= tolerancia:
            return medio, cota
        # Conservamos el intervalo con cambio de signo.
        if (fa > 0) != (fm > 0):
            b = medio
        else:
            a, fa = medio, fm
    raise ValueError('Se alcanzó el máximo sin cumplir la tolerancia.')


if __name__ == '__main__':
    raiz, cota = biseccion(lambda x: x*x - 2, 1, 2)
    print(f'Raíz aproximada: {raiz}; error absoluto acotado por {cota}')
