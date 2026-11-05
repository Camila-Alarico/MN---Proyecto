"""Programa del curso: única fuente para portada, barra lateral y recursos.

Antes esta lista estaba duplicada en `core.views.home` y escrita a mano en
`components/sidebar.html`. Para habilitar un módulo basta con poner `available=True`
y definir su `url`.
"""

MODULES = [
    {
        'number': 1,
        'title': 'Ecuaciones no lineales y errores',
        'description': 'Bisección, Newton-Raphson y más.',
        'icon': 'graph-up',
        'url': '/ecuaciones-no-lineales/',
        'available': True,
    },
    {
        'number': 2,
        'title': 'Sistemas de ecuaciones lineales',
        'description': 'Eliminación con pivoteo parcial y Gauss-Seidel.',
        'icon': 'grid-3x3',
        'url': '/sistemas-lineales/',
        'available': True,
    },
    {
        'number': 3,
        'title': 'Interpolación y ajuste de curvas',
        'description': 'Interpolación de Lagrange y regresión lineal.',
        'icon': 'bezier2',
        'url': None,
        'available': False,
    },
    {
        'number': 4,
        'title': 'Integración numérica',
        'description': 'Trapecio compuesto y Simpson compuesto.',
        'icon': 'bar-chart-steps',
        'url': None,
        'available': False,
    },
    {
        'number': 5,
        'title': 'Ecuaciones diferenciales',
        'description': 'Euler explícito y Runge-Kutta de orden 4.',
        'icon': 'activity',
        'url': None,
        'available': False,
    },
]

AVAILABLE_MODULES = [module for module in MODULES if module['available']]
