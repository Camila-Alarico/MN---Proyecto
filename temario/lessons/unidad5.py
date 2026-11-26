"""Unidad 5 · Integración y derivación numérica (semanas 12 y 13)."""

_POLY_TEX = r'f(x)=0.2+25x-200x^{2}+675x^{3}-900x^{4}+400x^{5}'

INTEGRACION = {
    'slug': 'integracion-numerica', 'title': 'Integración numérica: trapecio, Simpson y Romberg', 'icon': 'bar-chart-steps',
    'summary': 'Aproximar un área con trapecios o parábolas, mejorar el resultado por extrapolación e integrar en dos dimensiones.',
    'goals': ['Aplicar las reglas compuestas del trapecio y de Simpson 1/3 y 3/8.',
              'Relacionar el número de subintervalos con el orden del error.',
              'Construir la tabla de Romberg y calcular una integral doble por aplicación sucesiva de las reglas.'],
    'idea': [
        'Las <strong>fórmulas de Newton-Cotes</strong> reemplazan la función por un polinomio fácil de integrar. Con una '
        'recta entre dos puntos se obtiene la <strong>regla del trapecio</strong>; con una parábola por tres puntos, '
        '<strong>Simpson 1/3</strong>; con una cúbica por cuatro, <strong>Simpson 3/8</strong>.',
        r'Dividir el intervalo en \(n\) segmentos (regla compuesta) reduce el error: el trapecio es \(O(h^{2})\) y Simpson '
        r'\(O(h^{4})\). Simpson es exacto para polinomios hasta grado 3 aunque use parábolas.',
        '<strong>Romberg</strong> combina dos estimaciones del trapecio para cancelar el término principal del error '
        '(extrapolación de Richardson) y repite el proceso. Para una <strong>integral doble</strong> se integra primero en '
        'una dirección y luego en la otra con cualquiera de las reglas.',
    ],
    'formulas': [
        ('Trapecio compuesto', r'I\approx\frac{h}{2}\left[f(x_0)+2\sum_{i=1}^{n-1}f(x_i)+f(x_n)\right],\qquad h=\frac{b-a}{n}'),
        ('Simpson 1/3 compuesto (n par)', r'I\approx\frac{h}{3}\left[f(x_0)+4\!\!\sum_{i\ \text{impar}}\!\!f(x_i)+2\!\!\sum_{i\ \text{par}}\!\!f(x_i)+f(x_n)\right]'),
        ('Simpson 3/8', r'I\approx\frac{3h}{8}\left[f(x_0)+3f(x_1)+3f(x_2)+f(x_3)\right]'),
        ('Romberg', r'R_{i,k}=\frac{4^{k}R_{i,k-1}-R_{i-1,k-1}}{4^{k}-1}'),
        ('Integral doble', r'\int_{c}^{d}\!\!\int_{a}^{b}f(x,y)\,dx\,dy\approx\text{regla en }y\ \text{de}\ \Big[\text{regla en }x\ \text{de}\ f(x,y)\Big]'),
    ],
    'algorithm': [
        r'Elige \(n\) y calcula \(h=(b-a)/n\). Simpson 1/3 necesita \(n\) par; 3/8, múltiplo de 3.',
        r'Evalúa la función en los \(n+1\) nodos.',
        r'Aplica los pesos de la regla y multiplica por el factor (\(h/2\), \(h/3\) o \(3h/8\)).',
        r'Duplica \(n\) y compara: si el cambio es menor que la tolerancia, acepta el resultado.',
        r'Romberg: organiza los trapecios con \(n=1,2,4,\dots\) en la primera columna y extrapola hacia la derecha.',
    ],
    'example': {
        'title': 'Un polinomio de quinto grado entre 0 y 0.8',
        'statement': 'Integra f(x) de 0 a 0.8 con las tres reglas y con Romberg. Valor exacto: 1.640533.',
        'setup_tex': _POLY_TEX,
        'steps': [
            ('Trapecio.', 'Con n = 1: 0.8·(0.2 + 0.232)/2 = 0.172800 (error 89.5 %). Con n = 2: 1.068800. Con n = 4: 1.484800.'),
            ('Simpson 1/3.', 'Con n = 2: (0.4/3)·(0.2 + 4·2.456 + 0.232) = 1.367467 (error 16.6 %). Con n = 4: 1.623467 (1.0 %).'),
            ('Simpson 3/8.', 'Con n = 3: 1.519170 (error 7.4 %).'),
            ('Romberg.', 'R₁,₁ = (4·1.068800 − 0.172800)/3 = 1.367467; R₂,₁ = 1.623467; R₂,₂ = (16·1.623467 − 1.367467)/15 = 1.640533.'),
        ],
        'columns': ['n', 'Trapecio O(h²)', 'Columna 2 O(h⁴)', 'Columna 3 O(h⁶)'],
        'rows': [['1', '0.172800', '', ''], ['2', '1.068800', '1.367467', ''], ['4', '1.484800', '1.623467', '1.640533']],
        'conclusion': 'Con solo cinco evaluaciones de la función, Romberg recupera el valor exacto a seis decimales: combinar resultados mediocres da uno excelente.',
    },
    'pitfalls': [
        ('¿Simpson siempre gana al trapecio?', 'Para funciones suaves sí. Con datos ruidosos o funciones con picos, más segmentos de trapecio pueden ser más fiables.'),
        ('¿Puedo usar Simpson 1/3 con n impar?', 'No directamente. Se combina con Simpson 3/8 en los últimos tres segmentos.'),
        ('¿Aumentar n indefinidamente mejora siempre?', 'No: llega un punto en que el error de redondeo domina al de truncamiento.'),
    ],
    'lab': {'kind': 'integration', 'title': 'Área bajo la curva',
            'intro': 'Escribe la función y los límites. El área sombreada es lo que calcula la regla; compara su error con la referencia.'},
    'quiz': [
        {'q': 'Al duplicar el número de segmentos, el error del trapecio compuesto se divide aproximadamente entre…',
         'options': ['2', '4', '8', '16'], 'answer': 1, 'why': 'El error es O(h²): al dividir h entre 2, el error se divide entre 4.'},
        {'q': 'Simpson 1/3 es exacto para polinomios de grado hasta…',
         'options': ['1', '2', '3', '4'], 'answer': 2,
         'why': 'Aunque ajusta parábolas, el término de error depende de la cuarta derivada: es exacto hasta grado 3.'},
    ],
}

DERIVACION = {
    'slug': 'derivacion-numerica', 'title': 'Derivación numérica', 'icon': 'slash-lg',
    'summary': 'Estimar pendientes y curvaturas a partir de valores de la función: diferencias finitas y Richardson.',
    'goals': ['Deducir las fórmulas hacia adelante, hacia atrás y centrada a partir de la serie de Taylor.',
              'Obtener fórmulas de mayor exactitud y derivadas de orden superior.',
              'Mejorar una estimación con la extrapolación de Richardson y reconocer el efecto del redondeo.'],
    'idea': [
        'Derivar un <strong>polinomio de interpolación</strong> que pasa por puntos vecinos da una fórmula para la derivada: '
        'con dos puntos, la pendiente de la recta secante; con tres, la de una parábola.',
        'Las mismas fórmulas salen de la serie de Taylor, que además revela el error. La diferencia <strong>hacia adelante</strong> '
        r'y la <strong>hacia atrás</strong> son \(O(h)\); la <strong>centrada</strong> cancela un término y es \(O(h^{2})\). '
        'Usar más puntos cancela más términos y permite calcular <strong>derivadas de orden superior</strong>.',
        r'La <strong>extrapolación de Richardson</strong> automatiza la mejora: combina dos estimaciones con pasos \(h\) y '
        r'\(h/2\) para eliminar el término dominante del error. Cuidado: si \(h\) es demasiado pequeño, restar valores casi '
        'iguales amplifica el redondeo.',
    ],
    'formulas': [
        ('Hacia adelante', r"f'(x_i)\approx\frac{f(x_{i+1})-f(x_i)}{h}+O(h)"),
        ('Hacia atrás', r"f'(x_i)\approx\frac{f(x_i)-f(x_{i-1})}{h}+O(h)"),
        ('Centrada', r"f'(x_i)\approx\frac{f(x_{i+1})-f(x_{i-1})}{2h}+O(h^{2})"),
        ('Segunda derivada centrada', r"f''(x_i)\approx\frac{f(x_{i+1})-2f(x_i)+f(x_{i-1})}{h^{2}}+O(h^{2})"),
        ('Richardson', r'D\approx\frac{4}{3}D\!\left(\tfrac{h}{2}\right)-\frac{1}{3}D(h)'),
    ],
    'algorithm': [
        'Elige la fórmula según los puntos disponibles: centrada en el interior, hacia adelante o atrás en los bordes.',
        r'Evalúa la función en los puntos necesarios con paso \(h\).',
        r'Repite con \(h/2\) y combina ambas estimaciones con Richardson.',
        r'Si los datos tienen ruido, no reduzcas \(h\) sin límite: suaviza o ajusta antes de derivar.',
    ],
    'example': {
        'title': 'Derivada de un polinomio de cuarto grado en x = 0.5',
        'statement': 'Estima f′(0.5) con h = 0.5 y h = 0.25, y mejora el resultado con Richardson. Valor exacto: −0.9125.',
        'setup_tex': r'f(x)=-0.1x^{4}-0.15x^{3}-0.5x^{2}-0.25x+1.2',
        'steps': [
            ('Evaluar.', 'f(0) = 1.2, f(0.25) = 1.103516, f(0.5) = 0.925, f(0.75) = 0.636328, f(1) = 0.2.'),
            ('Con h = 0.5.', 'Adelante: (0.2 − 0.925)/0.5 = −1.45. Atrás: (0.925 − 1.2)/0.5 = −0.55. Centrada: (0.2 − 1.2)/1 = −1.0.'),
            ('Con h = 0.25.', 'Adelante: −1.154688. Atrás: −0.714063. Centrada: −0.934375 (error 2.4 %).'),
            ('Richardson.', 'D = (4/3)(−0.934375) − (1/3)(−1.0) = −0.9125: el valor exacto.'),
        ],
        'columns': ['Fórmula', 'h = 0.5', 'Error', 'h = 0.25', 'Error'],
        'rows': [['Hacia adelante O(h)', '−1.450000', '58.9 %', '−1.154688', '26.5 %'],
                 ['Hacia atrás O(h)', '−0.550000', '39.7 %', '−0.714063', '21.7 %'],
                 ['Centrada O(h²)', '−1.000000', '9.6 %', '−0.934375', '2.4 %'],
                 ['Richardson', '', '', '−0.912500', '0 %']],
        'conclusion': 'Al reducir h a la mitad, el error de las fórmulas O(h) cae a la mitad y el de la centrada a la cuarta parte. Richardson aprovecha ese patrón.',
    },
    'pitfalls': [
        ('¿Un h más pequeño siempre es mejor?', 'No. El truncamiento disminuye, pero el redondeo crece como 1/h. Existe un h óptimo.'),
        ('¿Por qué derivar es más delicado que integrar?', 'La integración promedia y suaviza los errores; la derivación resta valores cercanos y los amplifica.'),
        ('¿Qué fórmula uso en el borde de una tabla?', 'Una hacia adelante (o hacia atrás) de tres puntos, que mantiene el orden O(h²).'),
    ],
    'lab': {'kind': 'differentiation', 'title': 'Pendiente por diferencias finitas',
            'intro': 'Escribe la función, el punto y el paso. La gráfica muestra las secantes de cada fórmula y cómo cambia el error con h.'},
    'quiz': [
        {'q': '¿Cuál de estas fórmulas tiene error O(h²)?',
         'options': ['Hacia adelante de dos puntos', 'Hacia atrás de dos puntos', 'Centrada de dos puntos', 'Ninguna'],
         'answer': 2, 'why': 'En la diferencia centrada se cancela el término con la segunda derivada.'},
        {'q': 'Si h es extremadamente pequeño, la derivada numérica empeora porque…',
         'options': ['Crece el error de truncamiento', 'Crece el error de redondeo', 'La función deja de ser continua', 'La fórmula ya no es válida'],
         'answer': 1, 'why': 'Se restan valores casi iguales y se divide entre un número muy pequeño: el redondeo se amplifica.'},
    ],
}

LESSONS = [INTEGRACION, DERIVACION]
