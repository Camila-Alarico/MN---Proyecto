"""Registro único de navegación, métodos y parámetros del módulo 1.

Mapa de rutas del módulo (ver también `urls.py`): cada contenido tiene UNA sola URL canónica
`/ecuaciones-no-lineales/<slug>/`, donde <slug> sale de `TOPICS`. Todo enlace, tarjeta, buscador
o botón debe construirse con `{% url 'nonlinear:page' slug %}` (o `simulator_urls` en JS) y nunca
con una ruta escrita a mano.

Organización pedagógica (ver `ROUTE`): el estudiante recorre SEIS pasos, no once. Los seis
métodos siguen existiendo con su URL propia, pero se agrupan en dos familias (`FAMILIES`) y el
método concreto se elige dentro del simulador. Cada método incluye un ejercicio resuelto
(`WORKED_EXAMPLES`) que el estudiante puede reproducir en el laboratorio.
"""
METHODS = {
    'bisection': {'slug': 'biseccion', 'title': 'Bisección', 'icon': 'distribute-horizontal', 'difficulty': 'Inicial',
        'family': 'closed',
        'description': 'Encierra la raíz en un intervalo con cambio de signo y lo parte a la mitad.',
        'formula': r'x_m=\frac{a+b}{2}', 'parameters': ['a', 'b'], 'expression': 'x^3 - x - 2',
        'tip': 'Necesitas continuidad y cambio de signo. La anchura del intervalo se reduce a la mitad.'},
    'false-position': {'slug': 'regla-falsa', 'title': 'Regla falsa', 'icon': 'slash-lg', 'difficulty': 'Inicial',
        'family': 'closed',
        'description': 'Como bisección, pero el nuevo punto lo decide la recta que une los extremos.',
        'formula': r'x_r=a-\frac{f(a)(b-a)}{f(b)-f(a)}', 'parameters': ['a', 'b'], 'expression': 'x^3 - x - 2',
        'tip': 'Conserva el cambio de signo. Un extremo puede permanecer inmóvil durante muchas iteraciones.'},
    'fixed-point': {'slug': 'punto-fijo', 'title': 'Punto fijo', 'icon': 'arrow-repeat', 'difficulty': 'Intermedio',
        'family': 'open',
        'description': 'Reescribe f(x)=0 como x=g(x) y repite x←g(x).',
        'formula': r'x_{n+1}=g(x_n)', 'parameters': ['x0'], 'expression': 'cos(x)',
        'tip': '|g′(x)| < 1 es una orientación local, no una garantía global. Verifica que g represente la ecuación original.'},
    'newton': {'slug': 'newton', 'title': 'Newton-Raphson', 'icon': 'graph-up-arrow', 'difficulty': 'Intermedio',
        'family': 'open',
        'description': 'Sigue la tangente desde el punto actual hasta cortar el eje.',
        'formula': r'x_{n+1}=x_n-\frac{f(x_n)}{f\prime(x_n)}', 'parameters': ['x0'], 'expression': 'x^3 - x - 2',
        'tip': 'Una derivada pequeña vuelve inestable el paso. La convergencia depende del punto inicial.'},
    'secant': {'slug': 'secante', 'title': 'Secante', 'icon': 'bezier2', 'difficulty': 'Intermedio',
        'family': 'open',
        'description': 'Newton sin derivada: la pendiente se aproxima con los dos últimos puntos.',
        'formula': r'x_{n+1}=x_n-\frac{f(x_n)(x_n-x_{n-1})}{f(x_n)-f(x_{n-1})}',
        'parameters': ['x0', 'x1'], 'expression': 'x^3 - x - 2',
        'tip': 'Dos imágenes iguales producen un denominador nulo. No conserva necesariamente un intervalo.'},
    'multiple-roots': {'slug': 'raices-multiples', 'title': 'Raíces múltiples', 'icon': 'intersect', 'difficulty': 'Avanzado',
        'family': 'open',
        'description': 'Newton modificado: recupera la rapidez cuando f y f′ se anulan a la vez.',
        'formula': r'x_{n+1}=x_n-\frac{f(x_n)f\prime(x_n)}{[f\prime(x_n)]^2-f(x_n)f\prime\prime(x_n)}',
        'parameters': ['x0'], 'expression': '(x - 1)^3',
        'tip': 'En una raíz múltiple también se anula f′. Por ejemplo, (x−1)³ tiene multiplicidad 3 en x=1.'},
}

# Páginas de estudio con plantilla propia en templates/nonlinear/<slug>.html.
STUDY_PAGES = ('conceptos', 'errores', 'polinomios', 'busqueda', 'comparar')

TOPICS = [
    ('conceptos', 'Raíces de ecuaciones', 'lightbulb', 'Qué es una raíz y cuándo aceptar una aproximación.', 'Inicial'),
    ('errores', 'Errores numéricos', 'bullseye', 'Error absoluto, relativo y tolerancia.', 'Inicial'),
    ('polinomios', 'Raíces múltiples de polinomios', 'intersect', 'Cruce o contacto con el eje: qué cambia en Bisección y Newton.', 'Intermedio'),
    ('busqueda', 'Búsqueda gráfica', 'search', 'Mira la función antes de elegir intervalo o punto inicial.', 'Inicial'),
] + [(m['slug'], m['title'], m['icon'], m['description'], m['difficulty']) for m in METHODS.values()] + [
    ('comparar', 'Comparar métodos', 'bar-chart', 'Los métodos lado a lado: iteraciones, error y convergencia.', 'Intermedio'),
]

METHOD_BY_SLUG = {method['slug']: key for key, method in METHODS.items()}

# Método al que se envía el enlace heredado /laboratorio/ cuando no indica ?method=.
DEFAULT_METHOD = 'bisection'

TOPIC_SLUGS = frozenset(topic[0] for topic in TOPICS)

# --- Familias: el método se elige dentro del simulador ------------------------

FAMILIES = {
    'closed': {
        'title': 'Métodos cerrados', 'default': 'bisection',
        'description': 'Parten de un intervalo [a, b] con f(a)·f(b) < 0 y lo van estrechando. '
                       'Siempre convergen si f es continua, aunque suelen necesitar más pasos.',
    },
    'open': {
        'title': 'Métodos abiertos', 'default': 'newton',
        'description': 'Parten de uno o dos puntos iniciales, sin encerrar la raíz. Suelen ser más rápidos, '
                       'pero pueden divergir si el punto inicial no es adecuado.',
    },
}
for _key, _method in METHODS.items():
    FAMILIES[_method['family']].setdefault('methods', []).append({'key': _key, **_method})
FAMILY_LIST = [{'key': key, **family} for key, family in FAMILIES.items()]

# --- Ruta esencial: lo que ve el estudiante en la barra lateral ----------------
#
# Seis pasos en orden. `slugs` agrupa las páginas que cubre cada paso: el paso se marca como
# actual si el estudiante está en cualquiera de ellas y como completado si terminó alguna.
ROUTE = [
    {'slug': 'errores', 'title': 'Errores numéricos', 'icon': 'bullseye',
     'summary': 'Medir una aproximación y decidir si cumple la tolerancia.'},
    {'slug': 'conceptos', 'title': 'Raíces de ecuaciones', 'icon': 'lightbulb',
     'summary': 'Qué significa f(x) = 0 y qué permite aceptar una raíz.'},
    {'slug': 'biseccion', 'title': 'Métodos cerrados', 'icon': 'distribute-horizontal', 'family': 'closed',
     'summary': 'Bisección, con la regla falsa como variante. Un intervalo que siempre contiene la raíz.'},
    {'slug': 'newton', 'title': 'Métodos abiertos', 'icon': 'graph-up-arrow', 'family': 'open',
     'summary': 'Newton-Raphson, con punto fijo, secante y Newton modificado como alternativas.'},
    {'slug': 'polinomios', 'title': 'Raíces múltiples de polinomios', 'icon': 'intersect',
     'summary': 'Una raíz doble toca el eje sin cruzarlo: qué cambia en cada método.'},
    {'slug': 'comparar', 'title': 'Comparar métodos', 'icon': 'bar-chart',
     'summary': 'Los recorridos lado a lado: iteraciones, error y convergencia.'},
]
for _step in ROUTE:
    _family = FAMILIES.get(_step.get('family'))
    _step['slugs'] = [m['slug'] for m in _family['methods']] if _family else [_step['slug']]

ROUTE_SLUGS = frozenset(slug for step in ROUTE for slug in step['slugs'])
# Contenidos fuera de la ruta: herramientas de apoyo (hoy, la búsqueda gráfica).
TOOL_SLUGS = [slug for slug, *_ in TOPICS if slug not in ROUTE_SLUGS]

# --- Ejercicios resueltos --------------------------------------------------------
#
# Un ejercicio por método, con los valores calculados a mano (6 decimales) para que el estudiante
# pueda seguirlos en papel y luego reproducirlos en el simulador con `query`.

_CUBIC = r'f(x)=x^{3}-x-2,\qquad r\approx1.521380'

WORKED_EXAMPLES = {
    'bisection': {
        'title': 'Bisección en [1, 2]',
        'statement': 'Aproxima la raíz de f(x) = x³ − x − 2 en el intervalo [1, 2] con cuatro iteraciones.',
        'setup_tex': _CUBIC + r',\qquad f(1)=-2<0,\quad f(2)=4>0',
        'steps': [
            ('Comprobar el cambio de signo.', 'f(1) = −2 y f(2) = 4 tienen signos opuestos y f es continua: hay una raíz en [1, 2].'),
            ('Calcular el punto medio.', 'x₁ = (1 + 2)/2 = 1.5 y f(1.5) = −0.125 < 0. La raíz está en [1.5, 2].'),
            ('Repetir con el subintervalo que conserva el cambio de signo.', 'x₂ = 1.75, f(1.75) = 1.609 > 0 → [1.5, 1.75]; x₃ = 1.625 → [1.5, 1.625]; x₄ = 1.5625.'),
            ('Acotar el error.', 'Tras n pasos |xₙ − r| ≤ (b − a)/2ⁿ. Con n = 4 la cota es 1/16 = 0.0625.'),
        ],
        'columns': ['n', 'a', 'b', 'xₘ', 'f(xₘ)', '(b−a)/2'],
        'rows': [
            ['1', '1.000000', '2.000000', '1.500000', '−0.125000', '0.500000'],
            ['2', '1.500000', '2.000000', '1.750000', '1.609375', '0.250000'],
            ['3', '1.500000', '1.750000', '1.625000', '0.666016', '0.125000'],
            ['4', '1.500000', '1.625000', '1.562500', '0.252197', '0.062500'],
        ],
        'conclusion': 'Cada paso divide el error máximo entre dos: es seguro pero lento. Para una tolerancia de 10⁻⁴ harían falta unas 14 iteraciones.',
        'query': 'expression=x%5E3-x-2&a=1&b=2&tolerance=0.0001',
    },
    'false-position': {
        'title': 'Regla falsa en [1, 2]',
        'statement': 'Misma función e intervalo que en bisección, pero el nuevo punto es el corte de la recta que une (a, f(a)) y (b, f(b)).',
        'setup_tex': _CUBIC + r',\qquad x_r=b-\frac{f(b)(b-a)}{f(b)-f(a)}',
        'steps': [
            ('Primer corte.', 'x₁ = 2 − 4·(2 − 1)/(4 − (−2)) = 1.333333; f(x₁) = −0.962963 < 0, así que a pasa a ser 1.333333.'),
            ('Segundo corte.', 'x₂ = 1.462687, f(x₂) = −0.333339. El extremo b = 2 no se mueve.'),
            ('Tercer corte.', 'x₃ = 1.504019, f(x₃) = −0.101818. Las aproximaciones se acercan a la raíz solo por la izquierda.'),
        ],
        'columns': ['n', 'a', 'b', 'xᵣ', 'f(xᵣ)'],
        'rows': [
            ['1', '1.000000', '2.000000', '1.333333', '−0.962963'],
            ['2', '1.333333', '2.000000', '1.462687', '−0.333339'],
            ['3', '1.462687', '2.000000', '1.504019', '−0.101818'],
        ],
        'conclusion': 'Avanza más rápido que bisección al principio, pero como b queda fijo la anchura del intervalo no tiende a cero: no sirve como cota del error.',
        'query': 'expression=x%5E3-x-2&a=1&b=2&tolerance=0.0001',
    },
    'newton': {
        'title': 'Newton-Raphson desde x₀ = 1.5',
        'statement': 'Aproxima la raíz de f(x) = x³ − x − 2 partiendo de x₀ = 1.5, con f′(x) = 3x² − 1.',
        'setup_tex': _CUBIC + r",\qquad x_{n+1}=x_n-\frac{f(x_n)}{f'(x_n)}",
        'steps': [
            ('Evaluar f y f′ en x₀.', 'f(1.5) = −0.125 y f′(1.5) = 5.75.'),
            ('Aplicar la fórmula.', 'x₁ = 1.5 − (−0.125)/5.75 = 1.521739.'),
            ('Repetir.', 'f(x₁) = 0.002137 → x₂ = 1.521380; f(x₂) ≈ 10⁻⁶ → x₃ = 1.521380. Los decimales correctos se duplican en cada paso.'),
        ],
        'columns': ['n', 'xₙ', 'f(xₙ)', 'f′(xₙ)', 'xₙ₊₁'],
        'rows': [
            ['0', '1.500000', '−0.125000', '5.750000', '1.521739'],
            ['1', '1.521739', '0.002137', '5.947070', '1.521380'],
            ['2', '1.521380', '0.000001', '5.943790', '1.521380'],
        ],
        'conclusion': 'Tres iteraciones bastan para seis decimales: convergencia cuadrática. Requiere la derivada y un buen punto inicial (compara con x₀ = 0, donde f′ se acerca a cero).',
        'query': 'expression=x%5E3-x-2&x0=1.5&tolerance=0.0001',
    },
    'fixed-point': {
        'title': 'Punto fijo con g(x) = (x + 2)^(1/3)',
        'statement': 'De x³ − x − 2 = 0 se despeja x = (x + 2)^(1/3). Itera x ← g(x) desde x₀ = 1.5.',
        'setup_tex': r"g(x)=\sqrt[3]{x+2},\qquad g'(x)=\frac{1}{3}(x+2)^{-2/3},\qquad |g'(1.5)|\approx0.145<1",
        'steps': [
            ('Elegir una transformación que contraiga.', '|g′(x)| ≈ 0.145 cerca de la raíz: menor que 1, así que la iteración converge localmente.'),
            ('Iterar.', 'x₁ = g(1.5) = 1.518294; x₂ = 1.520935; x₃ = 1.521316; x₄ = 1.521370.'),
            ('Observar el ritmo.', 'El paso |xₙ₊₁ − xₙ| se reduce unas 7 veces por iteración (≈ 1/|g′|): convergencia lineal.'),
        ],
        'columns': ['n', 'xₙ', 'g(xₙ)', '|g(xₙ) − xₙ|'],
        'rows': [
            ['0', '1.500000', '1.518294', '0.018294'],
            ['1', '1.518294', '1.520935', '0.002641'],
            ['2', '1.520935', '1.521316', '0.000380'],
            ['3', '1.521316', '1.521370', '0.000055'],
        ],
        'conclusion': 'Con g(x) = x³ − 2 (otro despeje válido) |g′| ≈ 6.9 > 1 y la iteración diverge: la elección de g decide todo.',
        'query': 'expression=(x%2B2)%5E0.3333333333333333&x0=1.5&tolerance=0.0001',
    },
    'secant': {
        'title': 'Secante desde x₀ = 1, x₁ = 2',
        'statement': 'Aproxima la raíz de f(x) = x³ − x − 2 sin derivadas, usando la pendiente entre los dos últimos puntos.',
        'setup_tex': _CUBIC + r',\qquad x_{n+1}=x_n-\frac{f(x_n)(x_n-x_{n-1})}{f(x_n)-f(x_{n-1})}',
        'steps': [
            ('Primera secante.', 'Con (1, −2) y (2, 4): x₂ = 2 − 4·(2 − 1)/(4 + 2) = 1.333333.'),
            ('Seguir con los dos últimos puntos.', 'Con x₁ = 2 y x₂ = 1.333333: x₃ = 1.462687. Con x₂ y x₃: x₄ = 1.531169 (se pasa de la raíz).'),
            ('Una más.', 'x₅ = 1.520926, f(x₅) = −0.002693. A diferencia de la regla falsa, no conserva el intervalo.'),
        ],
        'columns': ['n', 'xₙ₋₁', 'xₙ', 'xₙ₊₁', 'f(xₙ₊₁)'],
        'rows': [
            ['1', '1.000000', '2.000000', '1.333333', '−0.962963'],
            ['2', '2.000000', '1.333333', '1.462687', '−0.333339'],
            ['3', '1.333333', '1.462687', '1.531169', '0.058626'],
            ['4', '1.462687', '1.531169', '1.520926', '−0.002693'],
        ],
        'conclusion': 'Converge con orden ≈ 1.618: más rápido que bisección, algo más lento que Newton, y sin calcular f′.',
        'query': 'expression=x%5E3-x-2&x0=1&x1=2&tolerance=0.0001',
    },
    'multiple-roots': {
        'title': 'Raíz doble de p(x) = (x − 1)²(x + 2) desde x₀ = 1.8',
        'statement': 'En x = 1 se anulan p y p′. Compara Newton ordinario con Newton modificado partiendo de 1.8.',
        'setup_tex': r"p(x)=x^{3}-3x+2,\quad p'(x)=3x^{2}-3,\quad p''(x)=6x,\qquad x_{n+1}=x_n-\frac{p\,p'}{(p')^{2}-p\,p''}",
        'steps': [
            ('Reconocer la multiplicidad.', 'p(1) = 0 y p′(1) = 0: raíz doble. Newton ordinario pierde la convergencia cuadrática (factor ≈ 1/2).'),
            ('Aplicar Newton modificado.', 'x₁ = 0.934959; x₂ = 0.999264; x₃ = 1.000000. Tres pasos para seis decimales.'),
            ('Contrastar con Newton ordinario.', 'Desde el mismo 1.8: 1.438095, 1.232168, 1.120108, 1.061188… el error se reduce solo a la mitad por paso.'),
        ],
        'columns': ['n', 'xₙ (modificado)', 'p(xₙ)', 'xₙ₊₁ (modificado)', 'xₙ₊₁ (Newton ordinario)'],
        'rows': [
            ['0', '1.800000', '2.432000', '0.934959', '1.438095'],
            ['1', '0.934959', '0.012416', '0.999264', '1.232168'],
            ['2', '0.999264', '0.000002', '1.000000', '1.120108'],
        ],
        'conclusion': 'Cuando f′(r) = 0, Newton modificado recupera la convergencia cuadrática. El precio es calcular también f″.',
        'query': 'expression=(x-1)%5E2*(x%2B2)&x0=1.8&tolerance=0.00000001',
    },
}
