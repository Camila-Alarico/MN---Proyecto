"""Ejecución validada de un método (único punto de entrada para `views.solve` y `views.compare`)."""
from nonlinear.services.parser import MathInputError

from ..catalog import METHODS
from ..forms import LinearSystemForm
from .direct import gauss_pivot
from .iterative import gauss_seidel


def _clean(method, data):
    if any(isinstance(value, bool) for value in data.values()):
        raise MathInputError('Los campos numéricos no aceptan valores booleanos.')
    form = LinearSystemForm(method, data)
    if not form.is_valid():
        raise MathInputError(' '.join(
            (f'{key}: ' if key != '__all__' else '') + ', '.join(errors) for key, errors in form.errors.items()))
    return form.cleaned_data


def _seidel(cleaned, direct):
    """Gauss-Seidel solo si la matriz no es singular: con A singular no hay solución única que aproximar."""
    if direct['singular']:
        return {'success': True, 'method': 'seidel', 'solution': None, 'residual': None, 'residual_vector': None,
                'converged': False, 'iterations': [], 'iterations_count': 0, 'status': 'Sistema singular',
                'message': 'La matriz es singular: no hay solución única y Gauss-Seidel no se ejecutó.',
                'dominance': None, 'convergence_note': ''}
    return gauss_seidel(cleaned['matrix'], cleaned['vector'], cleaned['tolerance'], cleaned['max_iterations'])


def run_system(method, data):
    """Valida `data`, ejecuta `method` y devuelve `(datos_limpios, respuesta)`."""
    if method not in METHODS:
        raise MathInputError('Método desconocido.')
    cleaned = _clean(method, data)
    direct = gauss_pivot(cleaned['matrix'], cleaned['vector'])
    return cleaned, direct if method == 'gauss' else _seidel(cleaned, direct)


def run_comparison(data):
    cleaned = _clean('seidel', data)
    direct = gauss_pivot(cleaned['matrix'], cleaned['vector'])
    iterative = _seidel(cleaned, direct)
    notes = []
    diff = None
    if direct['solution'] and iterative['solution']:
        diff = max(abs(a - b) for a, b in zip(direct['solution'], iterative['solution']))
        notes.append('Ambos métodos aportan solución; compara los residuos: un residuo pequeño no garantiza por sí solo un error pequeño.')
    elif direct['singular']:
        notes.append('Sistema singular: ningún método entrega una solución única.')
    elif not iterative['converged']:
        notes.append(f'Gauss-Seidel: {iterative["status"].lower()}. El método directo sí resolvió el sistema: '
                     'el iterativo depende de las propiedades de la matriz y del orden de las filas.')
    answer = {'success': True, 'method': 'compare', 'direct': direct, 'iterative': iterative,
              'difference_inf': diff, 'notes': notes,
              'status': 'Comparación', 'converged': bool(direct['solution'] and iterative['solution']),
              'iterations_count': iterative['iterations_count']}
    return cleaned, answer
