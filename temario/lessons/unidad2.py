"""Unidad 2 · Raíces de ecuaciones (semana 5: raíces de polinomios, métodos convencionales)."""

POLINOMIOS = {
    'slug': 'raices-polinomios', 'title': 'Raíces de polinomios: Horner, deflación y Müller', 'icon': 'diagram-3',
    'summary': 'Los métodos convencionales para hallar todas las raíces de un polinomio, una por una.',
    'goals': ['Evaluar un polinomio y su derivada con división sintética (regla de Horner).',
              'Aplicar Newton con división sintética (Birge-Vieta) y deflacionar para obtener las demás raíces.',
              'Reconocer cuándo conviene Müller o Bairstow (raíces complejas).'],
    'idea': [
        r'Un polinomio de grado \(n\) tiene exactamente \(n\) raíces, reales o complejas. Los métodos generales '
        '(bisección, Newton) encuentran una; los <strong>métodos convencionales para polinomios</strong> aprovechan su '
        'estructura para encontrarlas todas.',
        r'La <strong>regla de Horner</strong> evalúa \(p(x)\) con solo \(n\) multiplicaciones y, de paso, entrega el '
        r"cociente de dividir entre \((x-r)\). Repetirla sobre el cociente da \(p'(r)\): justo lo que Newton necesita.",
        r'Cuando se encuentra una raíz \(r\), se <strong>deflaciona</strong>: se reemplaza el polinomio por el cociente, de '
        'grado menor, y se busca la siguiente. Müller ajusta una parábola por tres puntos y puede llegar a raíces complejas; '
        'Bairstow extrae factores cuadráticos con aritmética real.',
    ],
    'formulas': [
        ('Regla de Horner', r'b_n=a_n,\qquad b_k=a_k+r\,b_{k+1},\qquad p(r)=b_0'),
        ('Birge-Vieta (Newton + Horner)', r"x_{i+1}=x_i-\frac{p(x_i)}{p'(x_i)}=x_i-\frac{b_0}{c_1}"),
        ('Deflación', r'p(x)=(x-r)\,q(x)+p(r),\qquad p(r)\approx0\;\Rightarrow\;p(x)\approx(x-r)\,q(x)'),
        ('Müller', r'x_3=x_2-\frac{2c}{b\pm\sqrt{b^{2}-4ac}}'),
    ],
    'algorithm': [
        r'Escribe los coeficientes de mayor a menor grado y elige un valor inicial \(x_0\).',
        r"Haz dos divisiones sintéticas seguidas: el primer residuo es \(p(x_i)\) y el segundo, \(p'(x_i)\).",
        r"Actualiza \(x_{i+1}=x_i-p(x_i)/p'(x_i)\) hasta que el cambio sea menor que la tolerancia.",
        'Deflaciona con la raíz encontrada y repite con el cociente. Al llegar a grado 2, usa la fórmula cuadrática.',
        'Refina cada raíz con el polinomio original para no acumular error de deflación.',
    ],
    'example': {
        'title': 'Todas las raíces de x³ − 6x² + 11x − 6',
        'statement': 'Encuentra una raíz con Birge-Vieta desde x₀ = 0.5 y obtén las demás por deflación.',
        'setup_tex': r"p(x)=x^{3}-6x^{2}+11x-6,\qquad x_{i+1}=x_i-\frac{p(x_i)}{p'(x_i)}",
        'steps': [
            ('Primera división sintética.', 'Con r = 0.5 sobre (1, −6, 11, −6): b = (1, −5.5, 8.25) y residuo p(0.5) = −1.875.'),
            ('Segunda división.', 'Con r = 0.5 sobre (1, −5.5, 8.25): residuo p′(0.5) = 5.75. Entonces x₁ = 0.5 + 1.875/5.75 = 0.826087.'),
            ('Iterar.', 'x₂ = 0.967693, x₃ = 0.998544, x₄ = 0.999997, x₅ = 1.000000. La raíz es r₁ = 1.'),
            ('Deflacionar.', 'Dividir entre (x − 1) deja q(x) = x² − 5x + 6, con residuo 0.'),
            ('Resolver el cociente.', 'x² − 5x + 6 = (x − 2)(x − 3): las otras raíces son 2 y 3.'),
        ],
        'columns': ['i', 'xᵢ', 'p(xᵢ)', 'p′(xᵢ)', 'xᵢ₊₁'],
        'rows': [['0', '0.500000', '−1.875000', '5.750000', '0.826087'], ['1', '0.826087', '−0.443823', '3.134216', '0.967693'],
                 ['2', '0.967693', '−0.067779', '2.196974', '0.998544'], ['3', '0.998544', '−0.002918', '2.008742', '0.999997'],
                 ['4', '0.999997', '−0.000006', '2.000019', '1.000000']],
        'conclusion': 'Una sola búsqueda iterativa más una deflación convierten un problema cúbico en uno cuadrático que se resuelve con fórmula.',
    },
    'pitfalls': [
        ('¿La deflación acumula error?', 'Sí. Cada raíz aproximada contamina el cociente. Por eso conviene extraer primero las raíces de menor magnitud y refinar cada una con el polinomio original.'),
        ('¿Y si las raíces son complejas?', 'Newton con valores reales nunca llega a ellas. Müller (con aritmética compleja) o Bairstow (factores cuadráticos) sí.'),
        ('¿Qué pasa con raíces múltiples?', 'p′ se anula en la raíz y Newton pierde velocidad. Consulta la lección de raíces múltiples.'),
    ],
    'lab': {'kind': 'polyroots', 'title': 'División sintética y deflación',
            'intro': 'Escribe los coeficientes de mayor a menor grado. El laboratorio busca una raíz, deflaciona y repite.'},
    'quiz': [
        {'q': 'Al dividir sintéticamente p(x) entre (x − r), el último número de la fila es…',
         'options': ['El grado del polinomio', 'p(r)', 'p′(r)', 'La raíz siguiente'],
         'answer': 1, 'why': 'Teorema del residuo: el residuo de dividir entre (x − r) es p(r).'},
        {'q': 'Después de hallar una raíz de un polinomio de grado 4 y deflacionar, queda un polinomio de grado…',
         'options': ['4', '3', '2', '1'], 'answer': 1,
         'why': 'Cada deflación reduce el grado en uno: de 4 a 3.'},
    ],
}

LESSONS = [POLINOMIOS]
