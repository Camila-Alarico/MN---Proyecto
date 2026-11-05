from decimal import Decimal, localcontext
import math

from .parser import finite, MathInputError


def calculate_errors(true_value, approximate_value, tolerance=None):
    true_value, approximate_value = finite(true_value), finite(approximate_value)
    # En esta actividad, los datos decimales introducidos son las referencias.
    # Evita que 1.1 − 1 se considere mayor que una tolerancia de 0.1.
    with localcontext() as context:
        context.prec = 340
        reference = Decimal(str(true_value))
        absolute_decimal = abs(reference - Decimal(str(approximate_value)))
        absolute = float(absolute_decimal)
        comparison = {}
        if tolerance is not None:
            try:
                if isinstance(tolerance, bool):
                    raise ValueError()
                tolerance = float(tolerance)
            except (ValueError, TypeError, OverflowError):
                raise MathInputError('Introduce una tolerancia absoluta finita y no negativa.') from None
            if not math.isfinite(tolerance) or tolerance < 0:
                raise MathInputError('La tolerancia absoluta debe ser no negativa.')
            limit = Decimal(str(tolerance))
            comparison = {'accepted': absolute_decimal <= limit,
                          'boundary_lower': float(reference-limit), 'boundary_upper': float(reference+limit)}
    relative = absolute / abs(true_value) if true_value != 0 else None
    overflow = relative is not None and (not math.isfinite(relative) or not math.isfinite(relative * 100))
    if overflow:
        relative = None
    return {'success': True, 'absolute': absolute, 'relative': relative,
            'percentage': relative * 100 if relative is not None else None,
            'message': f'El valor aproximado se encuentra {absolute:.8g} unidades del valor de referencia.' +
            (' Los errores relativo y porcentual exceden el rango numérico.' if overflow else
             ' El error relativo no está definido cuando el valor de referencia es cero.' if relative is None else ''),
            **comparison}
