"""Programa del curso: única fuente para portada, barra lateral y recursos.

Antes esta lista estaba duplicada en `core.views.home` y escrita a mano en
`components/sidebar.html`. Para habilitar un módulo basta con poner `available=True`
y definir su `url`. Los módulos 3 a 5 enlazan a sus unidades del temario
(`temario/catalog.py`), que organiza las 16 semanas del sílabo.
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
        'description': 'Regresión, interpolación de Newton y Lagrange, splines y Fourier.',
        'icon': 'bezier2',
        'url': '/temario/#unidad-5',
        'available': True,
    },
    {
        'number': 4,
        'title': 'Integración numérica',
        'description': 'Trapecio, Simpson, Romberg y derivación por diferencias finitas.',
        'icon': 'bar-chart-steps',
        'url': '/temario/#unidad-6',
        'available': True,
    },
    {
        'number': 5,
        'title': 'Ecuaciones diferenciales',
        'description': 'Euler, Euler modificado, Runge-Kutta e introducción a las EDP.',
        'icon': 'activity',
        'url': '/temario/#unidad-7',
        'available': True,
    },
]

AVAILABLE_MODULES = [module for module in MODULES if module['available']]
