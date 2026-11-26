"""Unidad 6 · Ecuaciones diferenciales (semanas 14 a 16)."""

_ODE_TEX = r"\frac{dy}{dt}=4e^{0.8t}-0.5y,\qquad y(0)=2"

EULER = {
    'slug': 'edo-euler', 'title': 'EDO: método de Euler y Euler modificado', 'icon': 'activity',
    'summary': 'Avanzar la solución de un problema de valor inicial con la pendiente local, y corregirla.',
    'goals': ['Explicar qué es un problema de valor inicial y por qué aparece en ingeniería.',
              'Aplicar el método de Euler y relacionar su error con el tamaño de paso.',
              'Mejorar la estimación con el método de Euler modificado (Heun, predictor-corrector).'],
    'idea': [
        'Las leyes de conservación se escriben como <strong>ecuaciones diferenciales</strong>: el enfriamiento de una pieza, '
        'la carga de un condensador, la caída de un paracaidista o el crecimiento de una población relacionan una magnitud '
        'con su ritmo de cambio. Pocas tienen solución analítica; el resto se resuelve numéricamente.',
        r"Un <strong>problema de valor inicial</strong> da la pendiente \(y'=f(t,y)\) y un punto de partida. El "
        r'<strong>método de Euler</strong> avanza un paso \(h\) siguiendo la tangente: es la serie de Taylor cortada tras '
        r'la primera derivada, con error local \(O(h^{2})\) y global \(O(h)\).',
        'El <strong>Euler modificado</strong> (Heun) no confía en una sola pendiente: predice con Euler, evalúa la pendiente '
        r'al final del intervalo y avanza con el promedio de ambas. Su error global es \(O(h^{2})\).',
    ],
    'formulas': [
        ('Problema de valor inicial', r"\frac{dy}{dt}=f(t,y),\qquad y(t_0)=y_0"),
        ('Euler', r'y_{i+1}=y_i+h\,f(t_i,y_i)'),
        ('Predictor (Heun)', r'y_{i+1}^{0}=y_i+h\,f(t_i,y_i)'),
        ('Corrector (Heun)', r'y_{i+1}=y_i+\frac{h}{2}\left[f(t_i,y_i)+f(t_{i+1},y_{i+1}^{0})\right]'),
        ('Punto medio', r'y_{i+1}=y_i+h\,f\!\left(t_i+\tfrac{h}{2},\;y_i+\tfrac{h}{2}f(t_i,y_i)\right)'),
    ],
    'algorithm': [
        r'Parte de \((t_0,y_0)\) y elige el paso \(h\).',
        r'Calcula la pendiente \(k_1=f(t_i,y_i)\).',
        r'Euler: \(y_{i+1}=y_i+h\,k_1\).',
        r'Heun: usa ese valor como predicción, calcula \(k_2=f(t_{i+1},y_{i+1}^{0})\) y corrige con \(y_{i+1}=y_i+h(k_1+k_2)/2\).',
        r'Avanza \(t_{i+1}=t_i+h\) y repite. Reduce \(h\) si la solución cambia rápido.',
    ],
    'example': {
        'title': 'Euler y Heun con paso h = 1',
        'statement': 'Integra de t = 0 a t = 4 con paso 1 y compara con la solución exacta y = (4/1.3)(e^{0.8t} − e^{−0.5t}) + 2e^{−0.5t}.',
        'setup_tex': _ODE_TEX,
        'steps': [
            ('Euler, primer paso.', 'k₁ = f(0, 2) = 4·1 − 0.5·2 = 3. y₁ = 2 + 1·3 = 5 (exacto 6.194631: error 19.3 %).'),
            ('Heun, predictor.', 'y₁⁰ = 5, el mismo valor de Euler.'),
            ('Heun, corrector.', 'k₂ = f(1, 5) = 4e^{0.8} − 2.5 = 6.402164. y₁ = 2 + (3 + 6.402164)/2 = 6.701082 (error 8.2 %).'),
            ('Continuar.', 'Se repite el procedimiento hasta t = 4. El error de Euler se acumula; el de Heun es menos de la mitad.'),
        ],
        'columns': ['t', 'Exacta', 'Euler', 'Error Euler', 'Heun', 'Error Heun'],
        'rows': [['0', '2.000000', '2.000000', '0 %', '2.000000', '0 %'],
                 ['1', '6.194631', '5.000000', '19.3 %', '6.701082', '8.2 %'],
                 ['2', '14.843922', '11.402164', '23.2 %', '16.319782', '9.9 %'],
                 ['3', '33.677172', '25.513212', '24.2 %', '37.199249', '10.5 %'],
                 ['4', '75.338963', '56.849311', '24.5 %', '83.337767', '10.6 %']],
        'conclusion': 'Promediar dos pendientes cuesta una evaluación más por paso y reduce el error a menos de la mitad. Con h = 0.5 ambos mejoran, Heun mucho más rápido.',
    },
    'pitfalls': [
        ('¿Por qué Euler se aleja cada vez más?', 'Cada paso parte de un valor ya equivocado: el error local se acumula en un error global proporcional a h.'),
        ('¿Basta reducir h?', 'Reduce el error, pero multiplica el trabajo. Suele ser mejor un método de orden mayor.'),
        ('¿Euler puede volverse inestable?', 'Sí. En ecuaciones rígidas, un paso grande hace que la solución numérica oscile y crezca aunque la real decaiga.'),
    ],
    'lab': {'kind': 'ode-euler', 'title': 'Sigue la pendiente',
            'intro': 'Escribe f(t, y), la condición inicial y el paso. Compara Euler, Heun y punto medio con la solución de referencia.'},
    'quiz': [
        {'q': 'El error global del método de Euler es proporcional a…',
         'options': ['h', 'h²', 'h³', 'h⁴'], 'answer': 0, 'why': 'El error local es O(h²) y se acumula en n = (b − a)/h pasos: el global es O(h).'},
        {'q': 'En el método de Heun, el valor final del paso se calcula con…',
         'options': ['La pendiente inicial', 'La pendiente final', 'El promedio de las pendientes inicial y final', 'La pendiente en el punto medio'],
         'answer': 2, 'why': 'Es un predictor-corrector: promedia la pendiente al inicio y la estimada al final.'},
    ],
}

RUNGE_KUTTA = {
    'slug': 'runge-kutta', 'title': 'Métodos de Runge-Kutta', 'icon': 'bezier',
    'summary': 'Combinar varias pendientes dentro del paso para ganar orden sin calcular derivadas superiores.',
    'goals': ['Reconocer Euler, Heun y punto medio como miembros de la familia Runge-Kutta.',
              'Aplicar el método clásico de cuarto orden (RK4).',
              'Comparar exactitud y costo de los métodos de distinto orden.'],
    'idea': [
        r'Todos los métodos de un paso tienen la misma forma: \(y_{i+1}=y_i+h\,\phi\), donde \(\phi\) es una pendiente '
        r'representativa del intervalo. Los <strong>métodos de Runge-Kutta</strong> construyen \(\phi\) como promedio '
        r'ponderado de varias pendientes \(k_j\) evaluadas en distintos puntos del paso.',
        'Con una pendiente se obtiene Euler (orden 1); con dos, Heun, punto medio o Ralston (orden 2). El '
        '<strong>RK4 clásico</strong> usa cuatro: una al inicio, dos en el punto medio y una al final, con pesos 1-2-2-1 '
        '(igual que la regla de Simpson).',
        r'Su error global es \(O(h^{4})\): reducir el paso a la mitad divide el error entre 16. Por eso RK4 es el método '
        r'de uso general: logra mucha exactitud con pasos relativamente grandes y solo necesita evaluar \(f\).',
    ],
    'formulas': [
        ('Forma general', r'y_{i+1}=y_i+h\,(a_1k_1+a_2k_2+\cdots+a_nk_n)'),
        ('Pendientes de RK4', r'k_1=f(t_i,y_i),\quad k_2=f\!\left(t_i+\tfrac{h}{2},y_i+\tfrac{h}{2}k_1\right),\quad k_3=f\!\left(t_i+\tfrac{h}{2},y_i+\tfrac{h}{2}k_2\right),\quad k_4=f(t_i+h,y_i+hk_3)'),
        ('Avance de RK4', r'y_{i+1}=y_i+\frac{h}{6}\left(k_1+2k_2+2k_3+k_4\right)'),
        ('RK3', r'y_{i+1}=y_i+\frac{h}{6}(k_1+4k_2+k_3),\qquad k_3=f(t_i+h,\;y_i-hk_1+2hk_2)'),
    ],
    'algorithm': [
        r'Calcula \(k_1\) con el punto actual.',
        r'Avanza medio paso con \(k_1\) y calcula \(k_2\).',
        r'Vuelve a avanzar medio paso, ahora con \(k_2\), y calcula \(k_3\).',
        r'Avanza el paso completo con \(k_3\) y calcula \(k_4\).',
        r'Combina: \(y_{i+1}=y_i+h(k_1+2k_2+2k_3+k_4)/6\).',
    ],
    'example': {
        'title': 'Un paso de RK4 y comparación de órdenes',
        'statement': 'Mismo problema de la lección de Euler, con h = 1. Valor exacto en t = 1: 6.194631.',
        'setup_tex': _ODE_TEX,
        'steps': [
            ('k₁.', 'k₁ = f(0, 2) = 4 − 1 = 3.'),
            ('k₂.', 'k₂ = f(0.5, 2 + 0.5·3) = 4e^{0.4} − 0.5·3.5 = 4.217299.'),
            ('k₃.', 'k₃ = f(0.5, 2 + 0.5·4.217299) = 4e^{0.4} − 0.5·4.108649 = 3.912974.'),
            ('k₄.', 'k₄ = f(1, 2 + 3.912974) = 4e^{0.8} − 0.5·5.912974 = 5.945677.'),
            ('Avance.', 'y₁ = 2 + (3 + 2·4.217299 + 2·3.912974 + 5.945677)/6 = 6.201037 (error 0.10 %).'),
        ],
        'columns': ['t', 'Exacta', 'Euler', 'Punto medio (RK2)', 'RK4', 'Error RK4'],
        'rows': [['1', '6.194631', '5.000000', '6.217299', '6.201037', '0.10 %'],
                 ['2', '14.843922', '11.402164', '14.940739', '14.862484', '0.13 %'],
                 ['3', '33.677172', '25.513212', '33.941154', '33.721348', '0.13 %'],
                 ['4', '75.338963', '56.849311', '75.968632', '75.439172', '0.13 %']],
        'conclusion': 'Con el mismo paso, Euler se equivoca en un 24 %, el punto medio en menos de 1 % y RK4 en 0.13 %. Cuatro evaluaciones por paso bien invertidas.',
    },
    'pitfalls': [
        ('¿RK4 es siempre la mejor opción?', 'Para problemas no rígidos y exactitud moderada, sí. En problemas rígidos se usan métodos implícitos.'),
        ('¿Cómo elegir h sin conocer la solución?', 'Comparando el resultado con h y con h/2, o con métodos adaptativos (Runge-Kutta-Fehlberg) que estiman el error en cada paso.'),
        ('¿Por qué los pesos 1-2-2-1?', 'Son los que hacen coincidir el método con la serie de Taylor hasta el término h⁴ sin calcular derivadas de f.'),
    ],
    'lab': {'kind': 'ode-rk', 'title': 'Compara los órdenes',
            'intro': 'Activa los métodos que quieras comparar. La gráfica inferior muestra el error de cada uno frente a la referencia, en escala logarítmica.'},
    'quiz': [
        {'q': '¿Cuántas evaluaciones de f necesita cada paso de RK4?',
         'options': ['1', '2', '3', '4'], 'answer': 3, 'why': 'Una por cada pendiente: k₁, k₂, k₃ y k₄.'},
        {'q': 'Si el paso de RK4 se reduce a la mitad, el error global se divide aproximadamente entre…',
         'options': ['2', '4', '8', '16'], 'answer': 3, 'why': 'El error global es O(h⁴): (1/2)⁴ = 1/16.'},
    ],
}

EDP = {
    'slug': 'edp-introduccion', 'title': 'Introducción a las ecuaciones en derivadas parciales', 'icon': 'grid-3x3',
    'summary': 'Clasificar una EDP y resolverla con diferencias finitas: placa en equilibrio y barra que se enfría.',
    'goals': ['Clasificar una EDP lineal de segundo orden como elíptica, parabólica o hiperbólica.',
              'Discretizar la ecuación de Laplace y resolverla con el método de Liebmann.',
              'Aplicar el esquema explícito a la ecuación de calor y respetar su condición de estabilidad.'],
    'idea': [
        'Cuando la incógnita depende de dos o más variables (posición y tiempo, o dos direcciones del espacio) aparece una '
        r'<strong>ecuación en derivadas parciales</strong>. Según el signo de \(B^{2}-4AC\) se clasifican en '
        '<strong>elípticas</strong> (equilibrio: Laplace), <strong>parabólicas</strong> (difusión: calor) e '
        '<strong>hiperbólicas</strong> (propagación: onda).',
        'El método de <strong>diferencias finitas</strong> cubre el dominio con una malla y reemplaza cada derivada por un '
        'cociente de diferencias. La EDP se convierte en ecuaciones algebraicas que relacionan cada nodo con sus vecinos.',
        'En la ecuación de Laplace, cada nodo interior es el <strong>promedio de sus cuatro vecinos</strong>; el sistema se '
        'resuelve iterando (Liebmann = Gauss-Seidel). En la ecuación de calor, el esquema explícito avanza en el tiempo, pero '
        r'solo es estable si \(\lambda=\alpha\,\Delta t/\Delta x^{2}\le 1/2\).',
    ],
    'formulas': [
        ('Clasificación', r'A\,u_{xx}+B\,u_{xy}+C\,u_{yy}+D=0:\quad B^{2}-4AC<0\ \text{elíptica},\ =0\ \text{parabólica},\ >0\ \text{hiperbólica}'),
        ('Laplace', r'\frac{\partial^{2}T}{\partial x^{2}}+\frac{\partial^{2}T}{\partial y^{2}}=0\quad\Rightarrow\quad T_{i,j}=\frac{T_{i+1,j}+T_{i-1,j}+T_{i,j+1}+T_{i,j-1}}{4}'),
        ('Sobrerrelajación', r'T_{i,j}^{\text{nuevo}}=\lambda\,T_{i,j}^{\text{nuevo}}+(1-\lambda)\,T_{i,j}^{\text{anterior}},\qquad 1\le\lambda<2'),
        ('Calor, esquema explícito', r'\frac{\partial T}{\partial t}=\alpha\frac{\partial^{2}T}{\partial x^{2}}\quad\Rightarrow\quad T_i^{\,l+1}=T_i^{\,l}+\lambda\left(T_{i+1}^{\,l}-2T_i^{\,l}+T_{i-1}^{\,l}\right)'),
        ('Estabilidad', r'\lambda=\frac{\alpha\,\Delta t}{\Delta x^{2}}\le\frac{1}{2}'),
    ],
    'algorithm': [
        'Clasifica la ecuación e identifica las condiciones de frontera (y la inicial, si depende del tiempo).',
        'Cubre el dominio con una malla y sustituye las derivadas por diferencias finitas.',
        'Elíptica: recorre los nodos interiores reemplazando cada uno por el promedio de sus vecinos hasta que el cambio máximo sea menor que la tolerancia.',
        r'Parabólica: calcula \(\lambda\); si es mayor que 1/2, reduce \(\Delta t\). Avanza capa por capa en el tiempo.',
    ],
    'example': {
        'title': 'Placa calentada con bordes a temperatura fija',
        'statement': 'Una placa cuadrada tiene el borde superior a 100 °C, el izquierdo a 75 °C, el derecho a 50 °C y el inferior a 0 °C. '
                     'Con una malla de 3 × 3 nodos interiores, halla las temperaturas de equilibrio.',
        'setup_tex': r'T_{i,j}=\frac{T_{i+1,j}+T_{i-1,j}+T_{i,j+1}+T_{i,j-1}}{4},\qquad i,j=1,2,3',
        'steps': [
            ('Plantear.', 'Hay 9 incógnitas. La ecuación del nodo inferior izquierdo es 4T₁₁ − T₂₁ − T₁₂ = 75 + 0.'),
            ('Iterar.', 'Se recorren los nodos con Gauss-Seidel partiendo del promedio de los bordes (56.25).'),
            ('Detenerse.', 'Tras 17 iteraciones el cambio máximo es menor que 10⁻⁴.'),
            ('Comprobar.', 'El nodo central vale 56.25 = (63.17 + 52.46 + 76.12 + 33.26)/4, salvo redondeo.'),
        ],
        'columns': ['Fila', 'Columna 1', 'Columna 2', 'Columna 3'],
        'rows': [['Superior (junto a 100 °C)', '78.57', '76.12', '69.64'],
                 ['Central', '63.17', '56.25', '52.46'],
                 ['Inferior (junto a 0 °C)', '42.86', '33.26', '33.93']],
        'conclusion': 'La temperatura cambia de forma suave entre los bordes: en equilibrio, cada punto es el promedio de sus vecinos.',
    },
    'pitfalls': [
        ('¿Por qué el esquema explícito «explota»?', 'Si λ > 1/2, los errores de redondeo se amplifican en cada paso de tiempo y aparecen oscilaciones crecientes.'),
        ('¿Cómo evitar la restricción de Δt?', 'Con esquemas implícitos (por ejemplo Crank-Nicolson), estables para cualquier paso a cambio de resolver un sistema tridiagonal por paso.'),
        ('¿Una malla más fina siempre conviene?', 'Mejora la exactitud, pero el número de incógnitas crece con el cuadrado y, en el esquema explícito, obliga a reducir Δt con Δx².'),
    ],
    'lab': {'kind': 'pde', 'title': 'Calor en una barra y en una placa',
            'intro': 'Elige el problema. En la barra, sube λ por encima de 0.5 para ver la inestabilidad; en la placa, cambia las temperaturas de los bordes.'},
    'quiz': [
        {'q': 'La ecuación de calor uₜ = α·uₓₓ es de tipo…',
         'options': ['Elíptico', 'Parabólico', 'Hiperbólico', 'Ordinario'], 'answer': 1,
         'why': 'Solo tiene una derivada segunda (en x): B² − 4AC = 0, parabólica.'},
        {'q': 'El esquema explícito para la ecuación de calor es estable si…',
         'options': ['λ ≤ 1/2', 'λ ≥ 1', 'λ = 2', 'Siempre'], 'answer': 0,
         'why': 'Con λ = αΔt/Δx² ≤ 1/2 los errores no crecen de un paso de tiempo al siguiente.'},
    ],
}

LESSONS = [EULER, RUNGE_KUTTA, EDP]
