"""Unidad 4 · Ajuste de curvas e interpolación (semanas 8 a 11)."""

REGRESION = {
    'slug': 'regresion-minimos-cuadrados', 'title': 'Regresión por mínimos cuadrados', 'icon': 'graph-up',
    'summary': 'La curva que mejor resume datos con ruido: recta, polinomio y modelos linealizados.',
    'goals': ['Obtener la recta de mínimos cuadrados a partir de las ecuaciones normales.',
              'Medir la calidad del ajuste con el error estándar y el coeficiente de determinación r².',
              'Extender la idea a polinomios y a modelos exponenciales o de potencia mediante linealización.'],
    'idea': [
        'Cuando los datos provienen de mediciones, traen error: no tiene sentido exigir que la curva pase por todos los '
        'puntos. La <strong>regresión</strong> busca la curva que sigue la tendencia general.',
        'El criterio de <strong>mínimos cuadrados</strong> elige los coeficientes que minimizan la suma de los cuadrados '
        r'de los residuos \(e_i=y_i-\hat y_i\). Elevar al cuadrado evita que errores positivos y negativos se cancelen '
        'y lleva a un sistema lineal: las <strong>ecuaciones normales</strong>.',
        r'El coeficiente \(r^{2}\) indica qué fracción de la variación de los datos explica el modelo. Un \(r^{2}\) alto no '
        'prueba que el modelo sea correcto: siempre hay que mirar la gráfica y los residuos.',
    ],
    'formulas': [
        ('Pendiente', r'a_1=\frac{n\sum x_iy_i-\sum x_i\sum y_i}{n\sum x_i^{2}-\left(\sum x_i\right)^{2}}'),
        ('Ordenada', r'a_0=\bar y-a_1\bar x'),
        ('Calidad del ajuste', r'S_r=\sum\left(y_i-a_0-a_1x_i\right)^{2},\qquad r^{2}=\frac{S_t-S_r}{S_t},\qquad s_{y/x}=\sqrt{\frac{S_r}{n-2}}'),
        ('Linealización', r'y=\alpha e^{\beta x}\Rightarrow\ln y=\ln\alpha+\beta x,\qquad y=\alpha x^{\beta}\Rightarrow\ln y=\ln\alpha+\beta\ln x'),
    ],
    'algorithm': [
        'Grafica los datos para elegir un modelo razonable (recta, parábola, exponencial…).',
        r'Calcula las sumas \(\sum x_i\), \(\sum y_i\), \(\sum x_iy_i\), \(\sum x_i^{2}\).',
        'Resuelve las ecuaciones normales para obtener los coeficientes.',
        r'Calcula \(S_t\), \(S_r\), \(r^{2}\) y el error estándar.',
        'Revisa los residuos: si muestran un patrón, el modelo no es adecuado.',
    ],
    'example': {
        'title': 'Ajustar una recta a siete mediciones',
        'statement': 'Ajusta una recta a los puntos (1, 0.5), (2, 2.5), (3, 2.0), (4, 4.0), (5, 3.5), (6, 6.0), (7, 5.5).',
        'setup_tex': r'n=7,\quad\sum x_i=28,\quad\sum y_i=24,\quad\sum x_iy_i=119.5,\quad\sum x_i^{2}=140',
        'steps': [
            ('Pendiente.', 'a₁ = (7·119.5 − 28·24)/(7·140 − 28²) = 164.5/196 = 0.839286.'),
            ('Ordenada.', 'a₀ = ȳ − a₁·x̄ = 3.428571 − 0.839286·4 = 0.071429.'),
            ('Calidad.', 'Sₜ = 22.714286 y Sᵣ = 2.991071: r² = 0.868318 y s = √(2.991071/5) = 0.773443.'),
            ('Interpretar.', 'La recta explica el 86.8 % de la variación de los datos.'),
        ],
        'columns': ['xᵢ', 'yᵢ', 'ŷᵢ = a₀ + a₁xᵢ', 'Residuo yᵢ − ŷᵢ'],
        'rows': [['1', '0.5', '0.910714', '−0.410714'], ['2', '2.5', '1.750000', '0.750000'],
                 ['3', '2.0', '2.589286', '−0.589286'], ['4', '4.0', '3.428571', '0.571429'],
                 ['5', '3.5', '4.267857', '−0.767857'], ['6', '6.0', '5.107143', '0.892857'],
                 ['7', '5.5', '5.946429', '−0.446429']],
        'conclusion': 'y = 0.071429 + 0.839286·x. Los residuos alternan de signo sin patrón: la recta es un modelo razonable.',
    },
    'pitfalls': [
        ('¿Regresión e interpolación son lo mismo?', 'No. La regresión no pasa por los puntos (hay ruido); la interpolación pasa exactamente por todos.'),
        ('¿Un r² cercano a 1 garantiza un buen modelo?', 'No. Datos curvos pueden dar r² alto con una recta. Mira siempre la gráfica de residuos.'),
        ('¿Se puede extrapolar?', 'Con mucha cautela: el ajuste solo está respaldado dentro del rango de los datos.'),
    ],
    'lab': {'kind': 'regression', 'title': 'Ajusta tus datos',
            'intro': 'Escribe un punto «x, y» por línea y elige el modelo. Las líneas verticales son los residuos que el método minimiza.'},
    'quiz': [
        {'q': 'El criterio de mínimos cuadrados minimiza…',
         'options': ['La suma de los residuos', 'La suma de los cuadrados de los residuos', 'El residuo máximo', 'La pendiente'],
         'answer': 1, 'why': 'Sᵣ = Σ(yᵢ − ŷᵢ)². Al elevar al cuadrado, los errores no se cancelan entre sí.'},
        {'q': 'Para ajustar y = α·e^(βx) con regresión lineal se grafica…',
         'options': ['y contra x', 'ln y contra x', 'ln y contra ln x', 'y contra ln x'],
         'answer': 1, 'why': 'ln y = ln α + βx es una recta en el plano (x, ln y).'},
    ],
}

INTERPOLACION = {
    'slug': 'interpolacion-newton', 'title': 'Interpolación polinómica: potencias y diferencias divididas', 'icon': 'bezier',
    'summary': 'El único polinomio que pasa por todos los puntos, escrito en tres formas equivalentes.',
    'goals': ['Plantear el polinomio interpolante en forma de serie de potencias (sistema de Vandermonde).',
              'Construir la tabla de diferencias divididas y el polinomio de Newton.',
              'Usar diferencias finitas cuando los datos están igualmente espaciados y estimar el error.'],
    'idea': [
        r'Por \(n+1\) puntos con abscisas distintas pasa <strong>un único</strong> polinomio de grado \(\le n\). Lo que '
        'cambia entre métodos es la forma de escribirlo y el trabajo para obtenerlo.',
        r'La <strong>forma de potencias</strong> \(a_0+a_1x+\dots+a_nx^{n}\) exige resolver un sistema lineal (de Vandermonde), '
        r'que se vuelve mal condicionado al crecer \(n\). El <strong>polinomio de Newton</strong> evita el sistema: sus '
        'coeficientes son <strong>diferencias divididas</strong> que se calculan en una tabla triangular.',
        'Si se agrega un punto, Newton solo añade un término y reutiliza todo lo anterior. Con datos igualmente espaciados '
        r'(paso \(h\)), las diferencias divididas se reducen a <strong>diferencias finitas</strong> \(\Delta^{k}f\).',
    ],
    'formulas': [
        ('Forma de potencias', r'p(x)=a_0+a_1x+\cdots+a_nx^{n},\qquad \sum_{k}a_k\,x_i^{k}=y_i'),
        ('Diferencias divididas', r'f[x_i,\dots,x_{i+k}]=\frac{f[x_{i+1},\dots,x_{i+k}]-f[x_i,\dots,x_{i+k-1}]}{x_{i+k}-x_i}'),
        ('Polinomio de Newton', r'p_n(x)=b_0+b_1(x-x_0)+b_2(x-x_0)(x-x_1)+\cdots,\qquad b_k=f[x_0,\dots,x_k]'),
        ('Diferencias finitas', r'f[x_0,\dots,x_k]=\frac{\Delta^{k}f_0}{k!\,h^{k}},\qquad \Delta f_i=f_{i+1}-f_i'),
        ('Error', r'R_n\approx f[x_0,\dots,x_{n+1}]\prod_{i=0}^{n}(x-x_i)'),
    ],
    'algorithm': [
        r'Ordena los puntos; la columna 0 de la tabla son los valores \(y_i\).',
        'Cada columna siguiente se obtiene restando dos vecinos de la anterior y dividiendo entre la diferencia de las abscisas extremas.',
        r'El primer elemento de cada columna es un coeficiente \(b_k\).',
        r'Evalúa el polinomio en forma anidada: \(p=b_n\); \(p\leftarrow p\,(x-x_k)+b_k\) para \(k=n-1,\dots,0\).',
        'El siguiente término (con un punto extra) estima el error de la interpolación.',
    ],
    'example': {
        'title': 'Estimar ln 2 con cuatro puntos',
        'statement': 'Con ln 1 = 0, ln 4 = 1.386294, ln 6 = 1.791759 y ln 5 = 1.609438, estima ln 2 (valor verdadero 0.693147).',
        'setup_tex': r'x_0=1,\;x_1=4,\;x_2=6,\;x_3=5,\qquad p_3(x)=b_0+b_1(x-1)+b_2(x-1)(x-4)+b_3(x-1)(x-4)(x-6)',
        'steps': [
            ('Primeras diferencias.', 'f[x₀,x₁] = 1.386294/3 = 0.462098; f[x₁,x₂] = 0.202733; f[x₂,x₃] = 0.182321.'),
            ('Segundas diferencias.', 'f[x₀,x₁,x₂] = (0.202733 − 0.462098)/(6 − 1) = −0.051873; f[x₁,x₂,x₃] = −0.020411.'),
            ('Tercera diferencia.', 'f[x₀,…,x₃] = (−0.020411 + 0.051873)/(5 − 1) = 0.007865.'),
            ('Evaluar en x = 2.', 'p₃(2) = 0 + 0.462098·1 − 0.051873·(1)(−2) + 0.007865·(1)(−2)(−4) = 0.628767.'),
        ],
        'columns': ['xᵢ', 'f(xᵢ)', 'Primera', 'Segunda', 'Tercera'],
        'rows': [['1', '0.000000', '0.462098', '−0.051873', '0.007865'],
                 ['4', '1.386294', '0.202733', '−0.020411', ''],
                 ['6', '1.791759', '0.182321', '', ''],
                 ['5', '1.609438', '', '', '']],
        'conclusion': 'El error baja de 33.3 % (lineal) a 18.4 % (cuadrático) y a 9.3 % (cúbico). Puntos más cercanos a x = 2 darían mucho mejor resultado.',
    },
    'pitfalls': [
        ('¿Newton y Lagrange dan polinomios distintos?', 'No: el polinomio interpolante es único. Solo cambia la forma de escribirlo y calcularlo.'),
        ('¿Más puntos siempre mejoran?', 'No. Con muchos puntos equiespaciados el polinomio oscila en los extremos (fenómeno de Runge). Para muchos datos se prefieren splines.'),
        ('¿Importa el orden de los puntos?', 'El polinomio final es el mismo, pero la tabla y los coeficientes intermedios cambian.'),
    ],
    'lab': {'kind': 'newtoninterp', 'title': 'Tabla de diferencias divididas',
            'intro': 'Escribe los puntos y el valor a interpolar. La tabla resalta los coeficientes del polinomio de Newton.'},
    'quiz': [
        {'q': '¿Cuántos puntos se necesitan para un polinomio interpolante de grado 3?',
         'options': ['2', '3', '4', '5'], 'answer': 2, 'why': 'Un polinomio de grado n queda determinado por n + 1 puntos: 4.'},
        {'q': 'Si se añade un punto nuevo a un polinomio de Newton…',
         'options': ['Hay que recalcular todo', 'Solo se añade un término', 'Baja el grado', 'El polinomio deja de pasar por los puntos anteriores'],
         'answer': 1, 'why': 'Los coeficientes anteriores no cambian; se calcula una diferencia dividida más.'},
    ],
}

LAGRANGE = {
    'slug': 'lagrange-splines', 'title': 'Polinomios de Lagrange y splines', 'icon': 'bezier2',
    'summary': 'Interpolar sin tabla de diferencias y, cuando hay muchos puntos, hacerlo por tramos suaves.',
    'goals': ['Escribir el polinomio interpolante como suma ponderada de polinomios base de Lagrange.',
              'Explicar por qué un polinomio de grado alto oscila y cómo lo evitan los splines.',
              'Construir un spline cúbico natural y evaluarlo.'],
    'idea': [
        r'El <strong>polinomio de Lagrange</strong> escribe el interpolante como \(\sum L_i(x)\,y_i\). Cada base \(L_i\) vale 1 '
        r'en su propio punto y 0 en los demás: es un «interruptor» que enciende el valor \(y_i\) donde corresponde.',
        'Un solo polinomio de grado alto que pase por muchos puntos puede oscilar mucho entre ellos. Los '
        '<strong>splines</strong> usan polinomios de grado bajo en cada tramo y los unen con suavidad.',
        'El <strong>spline cúbico</strong> exige que en cada nodo interior coincidan el valor, la pendiente y la curvatura. '
        'Eso lleva a un sistema tridiagonal para las segundas derivadas; el spline <em>natural</em> impone curvatura cero '
        'en los extremos, como una regla flexible apoyada en los puntos.',
    ],
    'formulas': [
        ('Polinomio de Lagrange', r'p_n(x)=\sum_{i=0}^{n}L_i(x)\,y_i,\qquad L_i(x)=\prod_{j\neq i}\frac{x-x_j}{x_i-x_j}'),
        ('Spline lineal', r's_i(x)=y_i+\frac{y_{i+1}-y_i}{x_{i+1}-x_i}(x-x_i)'),
        ('Spline cúbico por tramo', r's_i(x)=a_i+b_i(x-x_i)+c_i(x-x_i)^{2}+d_i(x-x_i)^{3}'),
        ('Sistema del spline natural', r"h_{i-1}M_{i-1}+2(h_{i-1}+h_i)M_i+h_iM_{i+1}=6\left(\frac{y_{i+1}-y_i}{h_i}-\frac{y_i-y_{i-1}}{h_{i-1}}\right),\quad M_0=M_n=0"),
    ],
    'algorithm': [
        r'Lagrange: para cada punto forma \(L_i(x)\) multiplicando los factores \((x-x_j)/(x_i-x_j)\) con \(j\ne i\).',
        r'Suma \(L_i(x)\,y_i\). Comprueba que \(\sum L_i(x)=1\).',
        r'Spline cúbico: calcula los anchos \(h_i\) y plantea el sistema tridiagonal de las segundas derivadas \(M_i\).',
        r'Resuélvelo (algoritmo de Thomas) con \(M_0=M_n=0\).',
        r'Con \(M_i\) obtén los coeficientes de cada tramo y evalúa en el tramo que contiene a \(x\).',
    ],
    'example': {
        'title': 'Lagrange de segundo grado para ln 2',
        'statement': 'Con los puntos (1, 0), (4, 1.386294) y (6, 1.791759), estima ln 2 con el polinomio de Lagrange de grado 2.',
        'setup_tex': r'p_2(2)=L_0(2)\,y_0+L_1(2)\,y_1+L_2(2)\,y_2',
        'steps': [
            ('Base L₀.', 'L₀(2) = (2 − 4)(2 − 6)/[(1 − 4)(1 − 6)] = 8/15 = 0.533333.'),
            ('Base L₁.', 'L₁(2) = (2 − 1)(2 − 6)/[(4 − 1)(4 − 6)] = −4/−6 = 0.666667.'),
            ('Base L₂.', 'L₂(2) = (2 − 1)(2 − 4)/[(6 − 1)(6 − 4)] = −2/10 = −0.2. Las tres suman 1.'),
            ('Combinar.', 'p₂(2) = 0.533333·0 + 0.666667·1.386294 − 0.2·1.791759 = 0.565844.'),
        ],
        'columns': ['i', 'xᵢ', 'yᵢ', 'Lᵢ(2)', 'Lᵢ(2)·yᵢ'],
        'rows': [['0', '1', '0.000000', '0.533333', '0.000000'], ['1', '4', '1.386294', '0.666667', '0.924196'],
                 ['2', '6', '1.791759', '−0.200000', '−0.358352'], ['Suma', '', '', '1.000000', '0.565844']],
        'conclusion': 'Es el mismo valor que da Newton con esos tres puntos: el polinomio es único. Para (3, 2.5), (4.5, 1), (7, 2.5), (9, 0.5), el spline cúbico natural da S(5) = 1.102890.',
    },
    'pitfalls': [
        ('¿Un peso de Lagrange puede ser negativo?', 'Sí (como L₂ = −0.2). Solo deben sumar 1.'),
        ('¿Por qué no usar siempre un polinomio de grado alto?', 'Porque oscila entre los nodos, sobre todo cerca de los extremos (fenómeno de Runge). El spline mantiene la curva pegada a los datos.'),
        ('¿Spline natural es la única opción?', 'No. También existen el spline sujeto (pendientes fijadas en los extremos) y el «not-a-knot».'),
    ],
    'lab': {'kind': 'splines', 'title': 'Lagrange frente a splines',
            'intro': 'Compara el polinomio único con los splines lineal y cúbico sobre los mismos puntos. Prueba el ejemplo de Runge.'},
    'quiz': [
        {'q': 'El polinomio base L₂(x) de Lagrange vale, en el nodo x₂…',
         'options': ['0', '1', 'y₂', 'Depende de los datos'], 'answer': 1,
         'why': 'Cada Lᵢ vale 1 en su nodo y 0 en los demás.'},
        {'q': 'Un spline cúbico garantiza en los nodos interiores la continuidad de…',
         'options': ['Solo el valor', 'Valor y primera derivada', 'Valor, primera y segunda derivada', 'Todas las derivadas'],
         'answer': 2, 'why': 'Se igualan valor, pendiente y curvatura; la tercera derivada puede saltar.'},
    ],
}

FOURIER = {
    'slug': 'aproximacion-fourier', 'title': 'Aproximación de Fourier', 'icon': 'soundwave',
    'summary': 'Representar una señal periódica como suma de senos y cosenos.',
    'goals': ['Calcular los coeficientes de la serie de Fourier de una función periódica.',
              'Interpretar cada armónico: frecuencia, amplitud y aporte a la forma de la señal.',
              'Reconocer el fenómeno de Gibbs y medir el error con el valor cuadrático medio.'],
    'idea': [
        'Los polinomios describen mal lo que se repite. Para vibraciones, señales eléctricas u ondas conviene otra base: '
        r'<strong>senos y cosenos</strong> de frecuencias múltiplos de una fundamental \(\omega_0=2\pi/T\).',
        'La <strong>serie de Fourier</strong> escribe una función periódica como un valor medio más una suma de armónicos. '
        'Cada coeficiente es la «proyección» de la función sobre un seno o un coseno: se obtiene con una integral en un periodo, '
        'y es justamente el ajuste de mínimos cuadrados con esa base.',
        'Cuantos más armónicos se suman, mejor es la aproximación. En las discontinuidades aparece un sobrepico de cerca del '
        '9 % que no desaparece al añadir términos: el <strong>fenómeno de Gibbs</strong>.',
    ],
    'formulas': [
        ('Serie de Fourier', r'f(t)\approx a_0+\sum_{k=1}^{N}\left[a_k\cos(k\omega_0t)+b_k\operatorname{sen}(k\omega_0t)\right],\qquad \omega_0=\frac{2\pi}{T}'),
        ('Valor medio', r'a_0=\frac{1}{T}\int_{0}^{T}f(t)\,dt'),
        ('Coeficientes', r'a_k=\frac{2}{T}\int_{0}^{T}f(t)\cos(k\omega_0t)\,dt,\qquad b_k=\frac{2}{T}\int_{0}^{T}f(t)\operatorname{sen}(k\omega_0t)\,dt'),
        ('Simetría', r'f\ \text{impar}\Rightarrow a_k=0,\qquad f\ \text{par}\Rightarrow b_k=0'),
    ],
    'algorithm': [
        r'Identifica el periodo \(T\) y la frecuencia fundamental \(\omega_0\).',
        'Aprovecha la simetría: si la función es impar solo hay senos; si es par, solo cosenos.',
        r'Calcula \(a_0\), \(a_k\) y \(b_k\) integrando en un periodo (analítica o numéricamente).',
        r'Suma los primeros \(N\) armónicos y compara con la función original.',
    ],
    'example': {
        'title': 'Onda cuadrada de amplitud 1',
        'statement': 'f(t) = −1 en (−π, 0) y f(t) = 1 en (0, π), con periodo 2π. Obtén los primeros armónicos.',
        'setup_tex': r'b_k=\frac{1}{\pi}\int_{-\pi}^{\pi}f(t)\operatorname{sen}(kt)\,dt=\frac{2}{\pi}\int_{0}^{\pi}\operatorname{sen}(kt)\,dt=\frac{2}{k\pi}\left(1-\cos k\pi\right)',
        'steps': [
            ('Simetría.', 'La función es impar: a₀ = 0 y todos los aₖ = 0. Solo hay términos en seno.'),
            ('Integrar.', 'bₖ = 2(1 − cos kπ)/(kπ): vale 4/(kπ) si k es impar y 0 si k es par.'),
            ('Evaluar.', 'b₁ = 4/π = 1.273240; b₃ = 4/(3π) = 0.424413; b₅ = 4/(5π) = 0.254648.'),
            ('Sumar.', 'f(t) ≈ 1.273240·sen t + 0.424413·sen 3t + 0.254648·sen 5t + …'),
        ],
        'columns': ['k', 'aₖ', 'bₖ', 'Aporte'],
        'rows': [['1', '0', '1.273240', 'Fundamental'], ['2', '0', '0', '—'], ['3', '0', '0.424413', 'Tercer armónico'],
                 ['4', '0', '0', '—'], ['5', '0', '0.254648', 'Quinto armónico']],
        'conclusion': 'Las amplitudes decaen como 1/k: la convergencia es lenta y cerca del salto queda el sobrepico de Gibbs.',
    },
    'pitfalls': [
        ('¿Añadir armónicos elimina el sobrepico?', 'No. El sobrepico de Gibbs se estrecha pero mantiene su altura (≈ 9 % del salto).'),
        ('¿Sirve para funciones no periódicas?', 'En un intervalo finito sí, entendiendo que la serie repite ese tramo. Para señales no periódicas se usa la transformada de Fourier.'),
        ('¿Por qué algunos coeficientes son cero?', 'Por simetría: las funciones impares no tienen cosenos y las pares no tienen senos.'),
    ],
    'lab': {'kind': 'fourier', 'title': 'Construye la señal con armónicos',
            'intro': 'Elige una onda y desliza el número de armónicos. Observa el espectro de amplitudes y el error cuadrático medio.'},
    'quiz': [
        {'q': 'La serie de Fourier de una función impar contiene…',
         'options': ['Solo cosenos', 'Solo senos', 'Senos y cosenos', 'Solo el valor medio'], 'answer': 1,
         'why': 'El producto de una función impar por un coseno (par) es impar y su integral en un periodo es cero.'},
        {'q': 'El coeficiente a₀ representa…',
         'options': ['La frecuencia fundamental', 'El valor medio de la función', 'La amplitud máxima', 'El periodo'],
         'answer': 1, 'why': 'a₀ = (1/T)∫f(t)dt es el promedio en un periodo.'},
    ],
}

LESSONS = [REGRESION, INTERPOLACION, LAGRANGE, FOURIER]
