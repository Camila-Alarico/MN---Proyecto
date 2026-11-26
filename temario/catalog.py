"""Temario completo del curso: seis unidades que agrupan las 16 semanas del sílabo.

Única fuente para `/temario/`, la portada, la barra lateral, la teoría y el buscador.
Cada semana conserva el texto del sílabo y enlaza a sus contenidos:

* `('lesson', slug)`: lección nueva de esta app (`temario/lessons/`), en `/temario/<slug>/`.
* `('nonlinear', slug)` / `('linear', slug)`: página ya existente de los módulos 1 y 2.

Los slugs son únicos en todo el curso: el avance de invitado vive en una sola lista de sesión.
"""
from linear.catalog import TOPICS as LINEAR_TOPICS
from nonlinear.catalog import TOPICS as NONLINEAR_TOPICS

from .lessons import LESSONS

UNITS = [
    {
        'number': 1, 'slug': 'errores', 'title': 'Errores',
        'icon': 'exclamation-triangle', 'accent': 'rose',
        'description': 'Tipos de error, cómo se propagan y cómo medirlos: error absoluto, relativo y tolerancia.',
        'weeks': [
            {'week': 1, 'title': 'Tipos de error y propagación de errores. Errores absoluto y relativo de números. '
                                 'Errores de redondeo y tolerancia.',
             'items': [('nonlinear', 'errores')]},
        ],
    },
    {
        'number': 2, 'slug': 'aproximacion', 'title': 'Aproximación',
        'icon': 'bullseye', 'accent': 'violet',
        'description': 'Qué significa aproximar: exactitud, precisión y la serie de Taylor con su error de truncamiento.',
        'weeks': [
            {'week': 2, 'title': 'Idea intuitiva de una aproximación. Exactitud y precisión. '
                                 'La serie de Taylor: errores de truncamiento, orden de aproximación. Aplicaciones.',
             'items': [('lesson', 'exactitud-precision'), ('lesson', 'serie-taylor')]},
        ],
    },
    {
        'number': 3, 'slug': 'raices-de-ecuaciones', 'title': 'Raíces de ecuaciones',
        'icon': 'graph-up', 'accent': 'blue',
        'description': 'Localizar y refinar las soluciones de f(x) = 0 con métodos cerrados, abiertos y para polinomios.',
        'weeks': [
            {'week': 3, 'title': 'Métodos gráficos, separación de las raíces analíticamente. '
                                 'Métodos cerrados: método de bisección, método de falsa posición.',
             'items': [('nonlinear', 'conceptos'), ('nonlinear', 'busqueda'), ('nonlinear', 'biseccion'),
                       ('nonlinear', 'regla-falsa')]},
            {'week': 4, 'title': 'Métodos abiertos: iteración de punto fijo, Newton-Raphson. Método de la secante.',
             'items': [('nonlinear', 'punto-fijo'), ('nonlinear', 'newton'), ('nonlinear', 'secante'),
                       ('nonlinear', 'comparar')]},
            {'week': 5, 'title': 'Raíces de polinomios, cálculo de las raíces de polinomios. Métodos convencionales.',
             'items': [('lesson', 'raices-polinomios'), ('nonlinear', 'polinomios'), ('nonlinear', 'raices-multiples')]},
        ],
    },
    {
        'number': 4, 'slug': 'sistemas-de-ecuaciones-lineales', 'title': 'Sistemas de ecuaciones lineales',
        'icon': 'grid-3x3', 'accent': 'teal',
        'description': 'Resolver A·x = b con métodos directos e iterativos, y saber cuándo conviene cada uno.',
        'weeks': [
            {'week': 6, 'title': 'Métodos directos. Eliminación de Gauss y Gauss-Jordan. '
                                 'Descomposición LU e inversión de matrices. Otros métodos.',
             'items': [('linear', 'formulacion'), ('linear', 'eliminacion-gaussiana'), ('lesson', 'gauss-jordan-inversa'),
                       ('lesson', 'descomposicion-lu')]},
            {'week': 7, 'title': 'Métodos iterativos. Matrices especiales y el método de Gauss-Seidel.',
             'items': [('lesson', 'jacobi-matrices-especiales'), ('linear', 'gauss-seidel'),
                       ('linear', 'comparacion-metodos')]},
        ],
    },
    {
        'number': 5, 'slug': 'ajuste-de-curvas', 'title': 'Ajuste de curvas e interpolación',
        'icon': 'bezier2', 'accent': 'amber',
        'description': 'Construir una función a partir de datos: la que mejor se ajusta o la que pasa por todos.',
        'weeks': [
            {'week': 8, 'title': 'Regresión por mínimos cuadrados. Problemas de aplicación y ejercicios.',
             'items': [('lesson', 'regresion-minimos-cuadrados')]},
            {'week': 9, 'title': 'Interpolación polinómica con forma de serie de potencias, '
                                 'con diferencias finitas y diferencias divididas.',
             'items': [('lesson', 'interpolacion-newton')]},
            {'week': 10, 'title': 'Polinomios de interpolación de Lagrange. Splines.',
             'items': [('lesson', 'lagrange-splines')]},
            {'week': 11, 'title': 'Aproximación de Fourier.',
             'items': [('lesson', 'aproximacion-fourier')]},
        ],
    },
    {
        'number': 6, 'slug': 'integracion-y-derivacion', 'title': 'Integración y derivación numérica',
        'icon': 'bar-chart-steps', 'accent': 'rose',
        'description': 'Aproximar áreas y pendientes cuando la función solo se conoce por puntos o es difícil de tratar.',
        'weeks': [
            {'week': 12, 'title': 'Reglas de Simpson y trapezoidal. Integración numérica en un dominio bidimensional. '
                                  'Integración de Romberg. Integración de ecuaciones de grado superior.',
             'items': [('lesson', 'integracion-numerica')]},
            {'week': 13, 'title': 'Derivación de polinomios de interpolación. Algoritmos para automatización de '
                                  'derivación. Evaluación numérica de derivadas de orden superior.',
             'items': [('lesson', 'derivacion-numerica')]},
        ],
    },
    {
        'number': 7, 'slug': 'ecuaciones-diferenciales', 'title': 'Ecuaciones diferenciales',
        'icon': 'activity', 'accent': 'green',
        'description': 'Avanzar una solución paso a paso: de Euler a Runge-Kutta y una primera mirada a las EDP.',
        'weeks': [
            {'week': 14, 'title': 'Introducción, uso de ecuaciones diferenciales en la ingeniería. Ecuaciones '
                                  'diferenciales ordinarias: método de Euler, método de Euler modificado. Ejemplos.',
             'items': [('lesson', 'edo-euler')]},
            {'week': 15, 'title': 'Métodos de Runge-Kutta.', 'items': [('lesson', 'runge-kutta')]},
            {'week': 16, 'title': 'Introducción de solución de EDP.', 'items': [('lesson', 'edp-introduccion')]},
        ],
    },
]

_EXISTING = {'nonlinear': {topic[0]: topic for topic in NONLINEAR_TOPICS},
             'linear': {topic[0]: topic for topic in LINEAR_TOPICS}}

# Lista plana en el orden del sílabo: sirve para «anterior / siguiente» y para el buscador.
SEQUENCE = []
for _unit in UNITS:
    _unit['first_week'], _unit['last_week'] = _unit['weeks'][0]['week'], _unit['weeks'][-1]['week']
    for _week in _unit['weeks']:
        _resolved = []
        for _kind, _slug in _week['items']:
            if _kind == 'lesson':
                _lesson = LESSONS[_slug]
                _lesson.update(unit=_unit['number'], week=_week['week'])
                _entry = {'kind': _kind, 'slug': _slug, 'title': _lesson['title'], 'icon': _lesson['icon'],
                          'summary': _lesson['summary'], 'is_new': True}
            else:
                _slug, _title, _icon, _description, _difficulty = _EXISTING[_kind][_slug]
                _entry = {'kind': _kind, 'slug': _slug, 'title': _title, 'icon': _icon,
                          'summary': _description, 'is_new': False}
            _entry.update(unit=_unit['number'], week=_week['week'])
            _resolved.append(_entry)
            SEQUENCE.append(_entry)
        _week['entries'] = _resolved

UNIT_BY_NUMBER = {unit['number']: unit for unit in UNITS}
LESSON_SLUGS = frozenset(LESSONS)
ALL_SLUGS = frozenset(entry['slug'] for entry in SEQUENCE)
TOTAL_WEEKS = sum(len(unit['weeks']) for unit in UNITS)
