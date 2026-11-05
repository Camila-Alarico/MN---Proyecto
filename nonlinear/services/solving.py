"""Ejecución validada de un método numérico.

Único punto de entrada para `views.solve` (un método) y `views.compare` (varios métodos), de modo
que ambos apliquen exactamente las mismas validaciones y el mismo criterio de punto fijo.
"""
from ..catalog import METHODS
from ..forms import CalculationForm
from .parser import MathInputError, parse_function
from .registry import calculate


def run_method(method, data, with_plot=True):
    """Valida `data`, ejecuta `method` y devuelve `(datos_limpios, respuesta)`.

    Para punto fijo, `expression` es g(x) y `reference_expression` (opcional) es la f(x) original:
    si g(x*) = x* pero f(x*) no es cero, g está mal planteada y la respuesta se marca sin convergencia.
    """
    if method not in METHODS:
        raise MathInputError('Método desconocido.')
    if any(isinstance(value, bool) for value in data.values()):
        raise MathInputError('Los campos numéricos no aceptan valores booleanos.')
    form = CalculationForm(method, data)
    if not form.is_valid():
        raise MathInputError(' '.join(f'{key}: {", ".join(errors)}' for key, errors in form.errors.items()))
    cleaned = form.cleaned_data
    answer = calculate(method, cleaned, with_plot=with_plot)
    if method == 'fixed-point' and data.get('reference_expression'):
        reference = parse_function(data['reference_expression'])
        residual = abs(reference(answer['root']))
        answer['reference_residual'] = residual
        if residual > cleaned['tolerance']:
            answer.update(
                converged=False, status='No convergió',
                message='El punto fijo no satisface f(x)=0 con la tolerancia pedida. Revisa la equivalencia de g(x).',
            )
    return cleaned, answer
