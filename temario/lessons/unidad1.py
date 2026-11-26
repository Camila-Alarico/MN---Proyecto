"""Unidad 1 · Aproximación y errores (semanas 1 y 2)."""

EXACTITUD = {
    'slug': 'exactitud-precision', 'title': 'Aproximación, exactitud y precisión', 'icon': 'bullseye',
    'summary': 'La idea intuitiva de aproximar: qué tan cerca del valor verdadero y qué tan repetible.',
    'goals': ['Explicar con tus palabras qué es una aproximación numérica.',
              'Distinguir exactitud (cercanía al valor verdadero) de precisión (cercanía entre mediciones).',
              'Relacionar el sesgo con el error y la dispersión con la incertidumbre.'],
    'idea': [
        r'Casi ningún cálculo de ingeniería usa números exactos: \(\pi\) se corta en 3.1416, una medición trae '
        'incertidumbre y un método iterativo se detiene antes del límite. <strong>Aproximar</strong> es aceptar un valor '
        'cercano al verdadero sabiendo <em>cuánto</em> nos alejamos.',
        'La <strong>exactitud</strong> indica qué tan cerca está el resultado del valor verdadero; la '
        '<strong>precisión</strong>, qué tan cerca están los resultados entre sí cuando se repite el cálculo o la medición. '
        'Son independientes: un instrumento mal calibrado puede ser muy preciso y poco exacto.',
        'En una diana, el centro es el valor verdadero. El desplazamiento del grupo de disparos respecto al centro es el '
        '<strong>sesgo</strong> (inexactitud); el tamaño del grupo es la <strong>dispersión</strong> (imprecisión).',
    ],
    'formulas': [
        ('Error verdadero', r'E_t=\text{valor verdadero}-\text{aproximación}'),
        ('Error relativo porcentual', r'\varepsilon_t=\left|\frac{E_t}{\text{valor verdadero}}\right|\cdot100\,\%'),
        ('Error aproximado (sin valor verdadero)', r'\varepsilon_a=\left|\frac{x_{\text{actual}}-x_{\text{anterior}}}{x_{\text{actual}}}\right|\cdot100\,\%'),
        ('Tolerancia para n cifras significativas', r'\varepsilon_s=(0.5\times10^{2-n})\,\%'),
    ],
    'algorithm': [
        'Identifica el valor de referencia (verdadero) si existe; si no, usa la aproximación anterior.',
        'Calcula el error absoluto y exprésalo relativo a la magnitud del valor.',
        r'Compara con la tolerancia: si \(\varepsilon_a<\varepsilon_s\), el resultado es correcto al menos en n cifras significativas.',
    ],
    'example': {
        'title': 'Medir un puente y un remache',
        'statement': 'Se mide un puente de 10 000 cm y se obtiene 9 999 cm; se mide un remache de 10 cm y se obtiene 9 cm. '
                     '¿Qué medición es mejor?',
        'setup_tex': r'E_t=\text{verdadero}-\text{medido},\qquad \varepsilon_t=\frac{|E_t|}{|\text{verdadero}|}\cdot 100\,\%',
        'steps': [
            ('Error absoluto.', 'Puente: 10 000 − 9 999 = 1 cm. Remache: 10 − 9 = 1 cm. Ambos se equivocan en 1 cm.'),
            ('Error relativo.', 'Puente: 1/10 000 = 0.01 %. Remache: 1/10 = 10 %.'),
            ('Interpretar.', 'El mismo centímetro es despreciable en el puente e inaceptable en el remache.'),
        ],
        'columns': ['Objeto', 'Verdadero (cm)', 'Medido (cm)', 'Error absoluto', 'Error relativo'],
        'rows': [['Puente', '10 000', '9 999', '1 cm', '0.01 %'], ['Remache', '10', '9', '1 cm', '10 %']],
        'conclusion': 'El error absoluto no basta para juzgar una aproximación: hay que compararlo con la magnitud de lo que se mide.',
    },
    'pitfalls': [
        ('¿Preciso significa exacto?', 'No. Diez mediciones casi idénticas pueden estar todas lejos del valor verdadero si hay un error sistemático (sesgo).'),
        ('¿Más decimales dan más exactitud?', 'No. Escribir 3.140000 no acerca el número a π; solo aparenta una precisión que no existe.'),
        ('¿Se puede medir el error sin conocer el valor verdadero?', 'Se estima con el error aproximado entre iteraciones sucesivas, que es un indicador, no el error real.'),
    ],
    'lab': {'kind': 'precision', 'title': 'Diana de exactitud y precisión',
            'intro': 'Mueve el sesgo y la dispersión. Observa cómo cambian el grupo de disparos y los dos indicadores.'},
    'quiz': [
        {'q': 'Una balanza marca siempre 2.05 kg, 2.05 kg y 2.06 kg para una pesa patrón de 2.00 kg. Es…',
         'options': ['Exacta y precisa', 'Precisa pero poco exacta', 'Exacta pero poco precisa', 'Ni exacta ni precisa'],
         'answer': 1, 'why': 'Los valores casi no varían (precisa) pero están desplazados 0.05 kg del patrón (sesgo: poco exacta).'},
        {'q': '¿Qué tolerancia garantiza al menos 3 cifras significativas correctas?',
         'options': ['0.5 %', '0.05 %', '0.005 %', '5 %'],
         'answer': 1, 'why': 'εs = 0.5 × 10^(2−3) % = 0.05 %.'},
    ],
}

TAYLOR = {
    'slug': 'serie-taylor', 'title': 'Serie de Taylor y error de truncamiento', 'icon': 'graph-up-arrow',
    'summary': 'Aproximar una función con un polinomio y saber cuánto se pierde al cortar la serie.',
    'goals': ['Construir el polinomio de Taylor de orden n alrededor de un punto a.',
              'Estimar el error de truncamiento con el residuo y leer su orden O(hⁿ⁺¹).',
              'Usar la serie para justificar fórmulas numéricas (derivadas, Euler, Newton).'],
    'idea': [
        r'Si se conoce una función y sus derivadas en un punto \(a\), se puede predecir su valor en un punto cercano '
        r'\(x=a+h\). Cada término añade información: el valor, la pendiente, la curvatura…',
        r'Al conservar solo los primeros \(n+1\) términos se comete un <strong>error de truncamiento</strong>. El residuo '
        r'\(R_n\) dice cuánto: es proporcional a \(h^{n+1}\), por eso se escribe \(O(h^{n+1})\). Reducir \(h\) a la '
        r'mitad divide el error entre \(2^{n+1}\), aproximadamente.',
        'Esta idea sostiene casi todo el curso: Newton-Raphson usa el orden 1, las diferencias finitas salen de restar '
        'series, y el método de Euler es la serie cortada después de la primera derivada.',
    ],
    'formulas': [
        ('Polinomio de Taylor', r'f(x)\approx\sum_{k=0}^{n}\frac{f^{(k)}(a)}{k!}(x-a)^{k}'),
        ('Residuo de Lagrange', r'R_n=\frac{f^{(n+1)}(\xi)}{(n+1)!}\,h^{\,n+1},\qquad \xi\in(a,x),\; h=x-a'),
        ('Orden de aproximación', r'f(a+h)=P_n(a+h)+O(h^{n+1})'),
    ],
    'algorithm': [
        r'Elige el punto de expansión \(a\) (donde conoces la función y sus derivadas) y calcula \(h=x-a\).',
        r'Evalúa las derivadas \(f^{(k)}(a)\) y suma los términos \(f^{(k)}(a)\,h^{k}/k!\) hasta el orden deseado.',
        r'Acota el residuo con el mayor valor posible de \(|f^{(n+1)}|\) en el intervalo y compara con la tolerancia.',
    ],
    'example': {
        'title': 'Aproximar e con la serie de Maclaurin',
        'statement': 'Aproxima e¹ con la serie de eˣ alrededor de a = 0 añadiendo un término cada vez. Valor verdadero: 2.718282.',
        'setup_tex': r'e^{x}\approx 1+x+\frac{x^{2}}{2!}+\frac{x^{3}}{3!}+\cdots+\frac{x^{n}}{n!},\qquad x=1',
        'steps': [
            ('Orden 0 y 1.', 'Con un término: 1 (error 1.718282). Con dos: 1 + 1 = 2 (error 0.718282).'),
            ('Añadir curvatura.', 'Orden 2: 2 + 1/2 = 2.5. Orden 3: 2.5 + 1/6 = 2.666667.'),
            ('Seguir hasta la tolerancia.', 'Orden 5: 2.716667, error 0.001615 (0.06 %). Cada término nuevo es menor que el anterior.'),
            ('Acotar con el residuo.', 'R₅ ≤ e¹/6! · 1⁶ ≈ 0.003775: el error real (0.001615) queda por debajo de la cota.'),
        ],
        'columns': ['Orden n', 'Término xⁿ/n!', 'Suma parcial', 'Error verdadero'],
        'rows': [['0', '1.000000', '1.000000', '1.718282'], ['1', '1.000000', '2.000000', '0.718282'],
                 ['2', '0.500000', '2.500000', '0.218282'], ['3', '0.166667', '2.666667', '0.051615'],
                 ['4', '0.041667', '2.708333', '0.009948'], ['5', '0.008333', '2.716667', '0.001615']],
        'conclusion': 'El error baja con cada término, pero nunca llega a cero con una cantidad finita: ese resto es el error de truncamiento.',
    },
    'pitfalls': [
        ('¿Más términos siempre mejoran?', 'Dentro del radio de convergencia sí. Fuera de él (por ejemplo ln(1 + x) con x > 1) la serie diverge y añadir términos empeora.'),
        ('¿Truncamiento es lo mismo que redondeo?', 'No. El truncamiento viene del método (cortar la serie); el redondeo, de la aritmética finita de la computadora.'),
        ('¿Qué significa O(h²)?', 'Que el error se comporta como una constante por h²: al dividir h entre 2, el error se divide aproximadamente entre 4.'),
    ],
    'lab': {'kind': 'taylor', 'title': 'Polinomio de Taylor interactivo',
            'intro': 'Elige la función, el punto de expansión y el orden. La curva punteada es el polinomio; la zona sombreada, el error.'},
    'quiz': [
        {'q': 'Un método tiene error O(h²). Si h se reduce de 0.1 a 0.05, el error aproximadamente…',
         'options': ['Se reduce a la mitad', 'Se reduce a la cuarta parte', 'No cambia', 'Se duplica'],
         'answer': 1, 'why': 'El error es proporcional a h²: (0.05/0.1)² = 1/4.'},
        {'q': 'El polinomio de Taylor de orden 1 de f alrededor de a es…',
         'options': ['Una constante', 'La recta tangente en a', 'Una parábola', 'La función exacta'],
         'answer': 1, 'why': 'f(a) + f′(a)(x − a) es la recta tangente: la base de Newton-Raphson y de Euler.'},
    ],
}

LESSONS = [EXACTITUD, TAYLOR]
