"""Registro único de navegación, métodos y casos del módulo 2 (sistemas de ecuaciones lineales).

Misma forma que `nonlinear/catalog.py`: cada contenido tiene UNA URL canónica
`/sistemas-lineales/<slug>/`. Los enlaces se construyen con `{% url 'linear:page' slug %}`.
Los slugs son únicos en todo el curso (no repiten los del módulo 1) porque el progreso de invitado
se guarda en una sola lista de sesión.

Organización pedagógica: los métodos se agrupan en dos familias (`FAMILIES`), directos e
iterativos, y el método concreto se elige dentro del laboratorio. Cada método trae un
ejercicio resuelto (`WORKED_EXAMPLES`) sobre el caso base.
"""
METHODS = {
    'gauss': {'slug': 'eliminacion-gaussiana', 'title': 'Eliminación gaussiana', 'icon': 'grid-3x3',
        'difficulty': 'Intermedio', 'parameters': [], 'family': 'direct',
        'description': 'Método directo: pivoteo parcial, eliminación hacia adelante y sustitución hacia atrás.',
        'formula': r'm_{ik}=\frac{a_{ik}^{(k)}}{a_{kk}^{(k)}},\quad x_i=\frac{c_i-\sum_{j>i}u_{ij}x_j}{u_{ii}}',
        'tip': 'Elige como pivote el elemento de mayor valor absoluto de la columna. Un pivote casi nulo indica un sistema singular o casi singular.'},
    'seidel': {'slug': 'gauss-seidel', 'title': 'Gauss-Seidel', 'icon': 'arrow-repeat',
        'difficulty': 'Intermedio', 'parameters': ['tolerance', 'max_iterations'], 'family': 'iterative',
        'description': 'Método iterativo: actualiza cada incógnita con los valores más recientes.',
        'formula': r'x_i^{(k+1)}=\frac{b_i-\sum_{j<i}a_{ij}x_j^{(k+1)}-\sum_{j>i}a_{ij}x_j^{(k)}}{a_{ii}}',
        'tip': 'La dominancia diagonal estricta es suficiente, no necesaria, para converger. Cambiar el orden de las filas puede cambiar el resultado.'},
}

# Páginas de estudio con plantilla propia en templates/linear/<slug>.html.
STUDY_PAGES = ('formulacion', 'comparacion-metodos')

TOPICS = [
    ('formulacion', 'Formulación y convergencia', 'lightbulb', 'Representa A·x = b y entiende cuándo converge Gauss-Seidel.', 'Inicial'),
] + [(m['slug'], m['title'], m['icon'], m['description'], m['difficulty']) for m in METHODS.values()] + [
    ('comparacion-metodos', 'Comparación directo vs. iterativo', 'bar-chart', 'Contrasta solución, residuo y procedimiento.', 'Intermedio'),
]

METHOD_BY_SLUG = {method['slug']: key for key, method in METHODS.items()}
DEFAULT_METHOD = 'gauss'
TOPIC_SLUGS = frozenset(topic[0] for topic in TOPICS)

# Prefijo con el que se guarda el método en CalculationHistory.method (máx. 30 caracteres).
HISTORY_PREFIX = 'linear-'
HISTORY_TITLES = {'linear-gauss': 'Sist. lineales · Gauss', 'linear-seidel': 'Sist. lineales · Seidel',
                  'linear-compare': 'Sist. lineales · Comparación'}

# --- Familias: el método se elige dentro del laboratorio ----------------------

FAMILIES = {
    'direct': {
        'title': 'Métodos directos', 'default': 'gauss',
        'description': 'Obtienen la solución exacta (salvo redondeo) en un número fijo de operaciones. '
                       'Fallan solo si el sistema es singular.',
    },
    'iterative': {
        'title': 'Métodos iterativos', 'default': 'seidel',
        'description': 'Parten de un vector inicial y mejoran la aproximación en cada paso. '
                       'Convergen solo bajo ciertas condiciones de la matriz y del orden de las filas.',
    },
}
for _key, _method in METHODS.items():
    FAMILIES[_method['family']].setdefault('methods', []).append({'key': _key, **_method})
FAMILY_LIST = [{'key': key, **family} for key, family in FAMILIES.items()]

# --- Ruta del módulo (barra lateral y portada) -----------------------------------
ROUTE = [
    {'slug': 'formulacion', 'title': 'Formulación y convergencia', 'icon': 'lightbulb',
     'summary': 'Representar A·x = b y saber cuándo confiar en cada método.'},
    {'slug': 'eliminacion-gaussiana', 'title': 'Métodos directos', 'icon': 'grid-3x3', 'family': 'direct',
     'summary': 'Eliminación gaussiana con pivoteo parcial: la solución en un número fijo de pasos.'},
    {'slug': 'gauss-seidel', 'title': 'Métodos iterativos', 'icon': 'arrow-repeat', 'family': 'iterative',
     'summary': 'Gauss-Seidel: aproximaciones sucesivas desde el vector cero.'},
    {'slug': 'comparacion-metodos', 'title': 'Comparar métodos', 'icon': 'bar-chart',
     'summary': 'Directo frente a iterativo: solución, residuo y procedimiento.'},
]
for _step in ROUTE:
    _family = FAMILIES.get(_step.get('family'))
    _step['slugs'] = [m['slug'] for m in _family['methods']] if _family else [_step['slug']]

# Casos del laboratorio. `meaning` explica qué representa cada incógnita.
EXAMPLES = {
    'base': {'title': 'Caso base: demanda de tres servicios', 'size': 3,
             'matrix': [[4, 1, 1], [1, 5, 1], [1, 1, 6]], 'vector': [9, 14, 21], 'solution': [1, 2, 3]},
    'permutado': {'title': 'Mismas ecuaciones, otro orden (exige intercambio de filas)', 'size': 3,
                  'matrix': [[1, 5, 1], [4, 1, 1], [1, 1, 6]], 'vector': [14, 9, 21], 'solution': [1, 2, 3]},
    'dos': {'title': 'Sistema 2×2', 'size': 2, 'matrix': [[3, 1], [1, 2]], 'vector': [9, 8], 'solution': [2, 3]},
    'sin-dominancia': {'title': '2×2 sin dominancia diagonal (Seidel converge)', 'size': 2,
                       'matrix': [[2, 3], [3, 6]], 'vector': [5, 9], 'solution': [1, 1]},
    'singular': {'title': 'Prueba de fallo: sistema singular', 'size': 2,
                 'matrix': [[1, 2], [2, 4]], 'vector': [3, 6], 'solution': None},
}

# --- Ejercicios resueltos (caso base, valores a seis decimales) -----------------

_BASE_TEX = (r'\begin{pmatrix}4&1&1\\1&5&1\\1&1&6\end{pmatrix}'
             r'\begin{pmatrix}x_1\\x_2\\x_3\end{pmatrix}=\begin{pmatrix}9\\14\\21\end{pmatrix}')
_BASE_QUERY = 'matrix=%5B%5B4%2C1%2C1%5D%2C%5B1%2C5%2C1%5D%2C%5B1%2C1%2C6%5D%5D&vector=%5B9%2C14%2C21%5D'

WORKED_EXAMPLES = {
    'gauss': {
        'title': 'Eliminación gaussiana sobre el caso base',
        'statement': 'Resuelve el sistema de demanda de tres servicios con pivoteo parcial y sustitución hacia atrás.',
        'setup_tex': _BASE_TEX,
        'steps': [
            ('Columna 1.', 'El mayor |aᵢ₁| ya está en la fila 1 (pivote 4): no hay intercambio. Multiplicadores m₂₁ = 1/4 = 0.25 y m₃₁ = 0.25. '
                           'F2 ← F2 − 0.25·F1 = (0, 4.75, 0.75 | 11.75); F3 ← F3 − 0.25·F1 = (0, 0.75, 5.75 | 18.75).'),
            ('Columna 2.', 'Pivote 4.75 (fila 2). m₃₂ = 0.75/4.75 = 0.157895. F3 ← F3 − 0.157895·F2 = (0, 0, 5.631579 | 16.894737).'),
            ('Sustitución hacia atrás.', 'x₃ = 16.894737/5.631579 = 3; x₂ = (11.75 − 0.75·3)/4.75 = 2; x₁ = (9 − 2 − 3)/4 = 1.'),
            ('Verificar.', 'Sustituye x = (1, 2, 3) en las tres ecuaciones: 9, 14 y 21. El residuo r = b − A·x es cero.'),
        ],
        'columns': ['Paso', 'Fila 1', 'Fila 2', 'Fila 3'],
        'rows': [
            ['[A | b]', '4  1  1 | 9', '1  5  1 | 14', '1  1  6 | 21'],
            ['Tras columna 1', '4  1  1 | 9', '0  4.75  0.75 | 11.75', '0  0.75  5.75 | 18.75'],
            ['Tras columna 2', '4  1  1 | 9', '0  4.75  0.75 | 11.75', '0  0  5.631579 | 16.894737'],
            ['Solución', 'x₁ = 1', 'x₂ = 2', 'x₃ = 3'],
        ],
        'conclusion': 'Dos columnas de eliminación y tres sustituciones: el costo es fijo y conocido de antemano. Prueba el ejemplo «otro orden» para ver el intercambio de filas.',
        'query': _BASE_QUERY,
    },
    'seidel': {
        'title': 'Gauss-Seidel sobre el caso base',
        'statement': 'Mismo sistema, partiendo de x⁽⁰⁾ = (0, 0, 0), tolerancia 10⁻⁶ y máximo 100 iteraciones.',
        'setup_tex': _BASE_TEX + r',\qquad x_i^{(k+1)}=\frac{b_i-\sum_{j<i}a_{ij}x_j^{(k+1)}-\sum_{j>i}a_{ij}x_j^{(k)}}{a_{ii}}',
        'steps': [
            ('Comprobar la dominancia diagonal.', '4 > 1 + 1, 5 > 1 + 1 y 6 > 1 + 1: es estricta por filas, así que la convergencia está garantizada desde cualquier inicio.'),
            ('Primera iteración.', 'x₁ = 9/4 = 2.25; x₂ = (14 − 2.25 − 0)/5 = 2.35 (usa el x₁ recién calculado); x₃ = (21 − 2.25 − 2.35)/6 = 2.733333.'),
            ('Seguir hasta la tolerancia.', 'El residuo ‖b − A·x‖∞ baja de 21 a 5.08, 0.26, 0.046… En la iteración 8 paso y residuo son ≤ 10⁻⁶ y se detiene.'),
        ],
        'columns': ['k', 'x₁', 'x₂', 'x₃', 'Paso ‖Δx‖∞', 'Residuo ‖r‖∞'],
        'rows': [
            ['0', '0.000000', '0.000000', '0.000000', '—', '21.000000'],
            ['1', '2.250000', '2.350000', '2.733333', '2.733333', '5.083333'],
            ['2', '0.979167', '2.057500', '2.993889', '1.270833', '0.260556'],
            ['3', '0.987153', '2.003792', '3.001509', '0.053708', '0.046088'],
            ['4', '0.998675', '1.999963', '3.000227', '0.011522', '0.005111'],
            ['…', '', '', '', '', ''],
            ['8', '1.000000', '2.000000', '3.000000', '0.000001', '0.000000'],
        ],
        'conclusion': 'Cada iteración reduce el residuo unas diez veces. Con las filas 1 y 2 intercambiadas se pierde la dominancia y el mismo método diverge: el orden importa.',
        'query': _BASE_QUERY,
    },
}
