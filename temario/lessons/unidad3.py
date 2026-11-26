"""Unidad 3 · Sistemas de ecuaciones lineales (semanas 6 y 7).

Los tres ejercicios usan el caso base del módulo 2 (demanda de tres servicios) para que se puedan
comparar con Eliminación gaussiana y Gauss-Seidel.
"""
_BASE_TEX = (r'\begin{pmatrix}4&1&1\1&5&1\1&1&6\end{pmatrix}'
             r'\begin{pmatrix}x_1\x_2\x_3\end{pmatrix}=\begin{pmatrix}9\14\21\end{pmatrix}')

GAUSS_JORDAN = {
    'slug': 'gauss-jordan-inversa', 'title': 'Gauss-Jordan e inversión de matrices', 'icon': 'grid-3x3-gap',
    'summary': 'Reducir [A | b] hasta la identidad para leer la solución, o [A | I] para obtener A⁻¹.',
    'goals': ['Aplicar Gauss-Jordan con pivoteo parcial hasta la forma escalonada reducida.',
              'Calcular la inversa de una matriz aumentándola con la identidad.',
              'Comparar el costo de Gauss-Jordan con la eliminación gaussiana.'],
    'idea': [
        'La eliminación de Gauss deja ceros <em>debajo</em> de la diagonal y termina con una sustitución hacia atrás. '
        '<strong>Gauss-Jordan</strong> elimina también <em>encima</em> de la diagonal y normaliza cada pivote a 1: la matriz '
        'se convierte en la identidad y la solución aparece directamente en la última columna.',
        r'El mismo procedimiento sobre \([A\,|\,I]\) produce \([I\,|\,A^{-1}]\). La inversa permite resolver muchos '
        r'sistemas con la misma matriz y distintos \(b\), y sus elementos indican cuánto responde cada incógnita a cada dato.',
        r'El precio: Gauss-Jordan hace alrededor de \(n^{3}/2\) operaciones frente a \(n^{3}/3\) de Gauss. Para un solo '
        r'sistema conviene Gauss; para la inversa o varios \(b\), Gauss-Jordan o LU.',
    ],
    'formulas': [
        ('Normalizar el pivote', r'F_k\leftarrow\frac{F_k}{a_{kk}}'),
        ('Eliminar en toda la columna', r'F_i\leftarrow F_i-a_{ik}\,F_k,\qquad i\neq k'),
        ('Inversa', r'[\,A\;|\;I\,]\;\longrightarrow\;[\,I\;|\;A^{-1}\,],\qquad x=A^{-1}b'),
    ],
    'algorithm': [
        r'Forma la matriz aumentada \([A\,|\,b]\) (o \([A\,|\,I]\) para la inversa).',
        r'Para cada columna \(k\): lleva a la fila \(k\) el elemento de mayor valor absoluto (pivoteo parcial).',
        r'Divide la fila \(k\) entre el pivote para dejar un 1 en la diagonal.',
        r'Resta a <em>todas</em> las demás filas el múltiplo necesario para anular su elemento en la columna \(k\).',
        'Al terminar, la parte izquierda es la identidad y la derecha contiene la solución (o la inversa).',
    ],
    'example': {
        'title': 'Gauss-Jordan sobre el caso base',
        'statement': 'Resuelve el sistema de demanda de tres servicios reduciendo la matriz aumentada hasta la identidad.',
        'setup_tex': _BASE_TEX,
        'steps': [
            ('Columna 1.', 'El pivote 4 ya es el mayor. F1 ← F1/4 = (1, 0.25, 0.25 | 2.25). Luego F2 ← F2 − F1 y F3 ← F3 − F1.'),
            ('Columna 2.', 'F2 ← F2/4.75 = (0, 1, 0.157895 | 2.473684). Se elimina arriba y abajo: F1 ← F1 − 0.25·F2, F3 ← F3 − 0.75·F2.'),
            ('Columna 3.', 'F3 ← F3/5.631579 = (0, 0, 1 | 3). F1 ← F1 − 0.210526·F3 y F2 ← F2 − 0.157895·F3.'),
            ('Leer la solución.', 'La matriz quedó [I | x] con x = (1, 2, 3). No hace falta sustitución hacia atrás.'),
        ],
        'columns': ['Paso', 'Fila 1', 'Fila 2', 'Fila 3'],
        'rows': [
            ['[A | b]', '4  1  1 | 9', '1  5  1 | 14', '1  1  6 | 21'],
            ['Tras columna 1', '1  0.25  0.25 | 2.25', '0  4.75  0.75 | 11.75', '0  0.75  5.75 | 18.75'],
            ['Tras columna 2', '1  0  0.210526 | 1.631579', '0  1  0.157895 | 2.473684', '0  0  5.631579 | 16.894737'],
            ['Tras columna 3', '1  0  0 | 1', '0  1  0 | 2', '0  0  1 | 3'],
        ],
        'conclusion': 'Aumentando con la identidad en vez de b se obtiene A⁻¹, cuya primera fila es (0.271028, −0.046729, −0.037383).',
    },
    'pitfalls': [
        ('¿Conviene calcular la inversa para resolver A·x = b?', 'Casi nunca: cuesta más y acumula más redondeo que la eliminación o LU. Se calcula cuando la inversa misma tiene interés.'),
        ('¿Toda matriz cuadrada tiene inversa?', 'No. Si aparece una columna sin pivote distinto de cero, la matriz es singular (determinante cero).'),
        ('¿El pivoteo cambia la solución?', 'No cambia la solución exacta; reduce el error de redondeo al evitar dividir entre números pequeños.'),
    ],
    'lab': {'kind': 'gaussjordan', 'title': 'Gauss-Jordan paso a paso',
            'intro': 'Escribe una fila por línea: los coeficientes y, tras «|», el término independiente. Recorre las operaciones de fila con el control deslizante.'},
    'quiz': [
        {'q': 'Al terminar Gauss-Jordan sobre [A | b], la parte izquierda es…',
         'options': ['Triangular superior', 'La matriz identidad', 'La inversa de A', 'Triangular inferior'],
         'answer': 1, 'why': 'Se eliminan los elementos encima y debajo de cada pivote normalizado: queda la identidad.'},
        {'q': 'Para obtener A⁻¹ con Gauss-Jordan se aumenta A con…',
         'options': ['El vector b', 'Una matriz de ceros', 'La matriz identidad', 'La transpuesta de A'],
         'answer': 2, 'why': '[A | I] se transforma en [I | A⁻¹].'},
    ],
}

LU = {
    'slug': 'descomposicion-lu', 'title': 'Descomposición LU', 'icon': 'layers',
    'summary': 'Factorizar A = L·U una vez y resolver después cualquier b con dos sustituciones.',
    'goals': ['Obtener L y U a partir de los multiplicadores de la eliminación gaussiana.',
              'Resolver A·x = b con sustitución hacia adelante (L·d = b) y hacia atrás (U·x = d).',
              'Usar la factorización para varios b, el determinante y la inversa.'],
    'idea': [
        r'Durante la eliminación de Gauss se calculan multiplicadores \(m_{ik}\) y luego se descartan. La '
        r'<strong>descomposición LU</strong> los guarda: forman una matriz triangular inferior \(L\) con unos en la diagonal, '
        r'y la matriz triangular superior que resulta de la eliminación es \(U\). Se cumple \(A=LU\).',
        r'Resolver \(Ax=b\) se vuelve dos problemas triangulares baratos: primero \(Ld=b\) hacia adelante y luego '
        r'\(Ux=d\) hacia atrás. La parte cara (factorizar, \(\sim n^{3}/3\)) se hace una sola vez; cada nuevo \(b\) cuesta '
        r'solo \(\sim n^{2}\).',
        r'Con pivoteo parcial se factoriza una permutación de filas: \(PA=LU\). Otros métodos de la misma familia: '
        r'Crout (unos en la diagonal de \(U\)) y Cholesky (\(A=LL^{T}\) para matrices simétricas definidas positivas).',
    ],
    'formulas': [
        ('Factorización de Doolittle', r'A=LU,\qquad l_{ii}=1,\qquad l_{ik}=\frac{a_{ik}^{(k)}}{a_{kk}^{(k)}}'),
        ('Sustitución hacia adelante', r'd_i=b_i-\sum_{j<i}l_{ij}\,d_j'),
        ('Sustitución hacia atrás', r'x_i=\frac{d_i-\sum_{j>i}u_{ij}\,x_j}{u_{ii}}'),
        ('Determinante', r'\det(A)=(-1)^{p}\prod_{i}u_{ii}\qquad(p=\text{número de intercambios})'),
    ],
    'algorithm': [
        r'Aplica la eliminación de Gauss a \(A\) y guarda cada multiplicador \(l_{ik}\) en la posición que acaba de anular.',
        r'La matriz final de la eliminación es \(U\); los multiplicadores, con unos en la diagonal, forman \(L\).',
        r'Resuelve \(Ld=b\) de arriba hacia abajo.',
        r'Resuelve \(Ux=d\) de abajo hacia arriba.',
        r'Para otro vector \(b\), repite solo los dos últimos pasos.',
    ],
    'example': {
        'title': 'LU del caso base y solución en dos sustituciones',
        'statement': 'Factoriza la matriz del sistema de demanda y resuélvelo para b = (9, 14, 21).',
        'setup_tex': _BASE_TEX,
        'steps': [
            ('Columna 1.', 'l₂₁ = 1/4 = 0.25 y l₃₁ = 1/4 = 0.25. Las filas 2 y 3 pasan a (0, 4.75, 0.75) y (0, 0.75, 5.75).'),
            ('Columna 2.', 'l₃₂ = 0.75/4.75 = 0.157895. La fila 3 pasa a (0, 0, 5.631579).'),
            ('Sustitución hacia adelante.', 'd₁ = 9; d₂ = 14 − 0.25·9 = 11.75; d₃ = 21 − 0.25·9 − 0.157895·11.75 = 16.894737.'),
            ('Sustitución hacia atrás.', 'x₃ = 16.894737/5.631579 = 3; x₂ = (11.75 − 0.75·3)/4.75 = 2; x₁ = (9 − 2 − 3)/4 = 1.'),
            ('Determinante.', 'det(A) = 4 · 4.75 · 5.631579 = 107 (no hubo intercambios de filas).'),
        ],
        'columns': ['Matriz', 'Fila 1', 'Fila 2', 'Fila 3'],
        'rows': [
            ['L', '1  0  0', '0.25  1  0', '0.25  0.157895  1'],
            ['U', '4  1  1', '0  4.75  0.75', '0  0  5.631579'],
            ['d (L·d = b)', '9', '11.75', '16.894737'],
            ['x (U·x = d)', '1', '2', '3'],
        ],
        'conclusion': 'L y U son los mismos números de la eliminación gaussiana, solo que guardados. Con otro b bastan dos sustituciones.',
    },
    'pitfalls': [
        ('¿LU es un método distinto de Gauss?', 'Es la misma eliminación organizada para reutilizarla: los multiplicadores se conservan en L.'),
        ('¿Siempre existe A = LU?', 'Sin intercambios puede fallar si aparece un pivote cero. Con pivoteo parcial, PA = LU existe para toda matriz no singular.'),
        ('¿Cuándo usar Cholesky?', 'Cuando A es simétrica y definida positiva: requiere la mitad de operaciones y no necesita pivoteo.'),
    ],
    'lab': {'kind': 'lu', 'title': 'Factoriza y resuelve',
            'intro': 'Escribe el sistema. Se muestran L, U, los multiplicadores y las dos sustituciones. Comprueba que L·U reproduce A.'},
    'quiz': [
        {'q': 'En la descomposición de Doolittle, los elementos bajo la diagonal de L son…',
         'options': ['Los pivotes', 'Los multiplicadores de la eliminación', 'Los residuos', 'Ceros'],
         'answer': 1, 'why': 'l_ik es el factor con el que se anuló a_ik durante la eliminación.'},
        {'q': 'Se deben resolver 50 sistemas con la misma matriz A y distintos b. Lo más eficiente es…',
         'options': ['Eliminación de Gauss 50 veces', 'Factorizar LU una vez y sustituir 50 veces', 'Gauss-Jordan 50 veces', 'Calcular 50 determinantes'],
         'answer': 1, 'why': 'La factorización (lo costoso) se hace una vez; cada b solo necesita dos sustituciones de orden n².'},
    ],
}

JACOBI = {
    'slug': 'jacobi-matrices-especiales', 'title': 'Jacobi, relajación y matrices especiales', 'icon': 'arrow-repeat',
    'summary': 'Métodos iterativos frente a frente y las matrices (tridiagonales, simétricas) que admiten atajos.',
    'goals': ['Aplicar el método de Jacobi y compararlo con Gauss-Seidel.',
              'Usar la dominancia diagonal como criterio suficiente de convergencia y la relajación para acelerarla.',
              'Reconocer matrices bandeadas y simétricas, y resolver un sistema tridiagonal con el algoritmo de Thomas.'],
    'idea': [
        'Un método iterativo despeja cada incógnita de su ecuación y repite. <strong>Jacobi</strong> calcula todas las '
        'incógnitas nuevas con los valores de la iteración anterior; <strong>Gauss-Seidel</strong> usa cada valor nuevo '
        'en cuanto lo obtiene, y por eso suele converger en menos iteraciones.',
        r'Ambos convergen con seguridad si la matriz es <strong>diagonalmente dominante</strong> (cada \(|a_{ii}|\) supera '
        'la suma de los demás valores absolutos de su fila). La <strong>relajación</strong> mezcla el valor nuevo con el '
        r'anterior: \(\lambda>1\) acelera sistemas que ya convergen; \(\lambda<1\) amortigua oscilaciones.',
        'Muchos problemas de ingeniería producen <strong>matrices especiales</strong>: bandeadas o tridiagonales (cada '
        'ecuación relaciona solo nodos vecinos) y simétricas. El algoritmo de Thomas resuelve un sistema tridiagonal en '
        r'\(O(n)\) operaciones; Cholesky aprovecha la simetría.',
    ],
    'formulas': [
        ('Jacobi', r'x_i^{(k+1)}=\frac{b_i-\sum_{j\neq i}a_{ij}\,x_j^{(k)}}{a_{ii}}'),
        ('Gauss-Seidel con relajación', r'x_i^{\text{nuevo}}=\lambda\,x_i^{\text{GS}}+(1-\lambda)\,x_i^{\text{anterior}},\qquad 0<\lambda<2'),
        ('Dominancia diagonal', r'|a_{ii}|>\sum_{j\neq i}|a_{ij}|\quad\text{para toda fila } i'),
        ('Thomas (tridiagonal)', r"c'_i=\frac{c_i}{b_i-a_i c'_{i-1}},\qquad d'_i=\frac{d_i-a_i d'_{i-1}}{b_i-a_i c'_{i-1}},\qquad x_i=d'_i-c'_i x_{i+1}"),
    ],
    'algorithm': [
        'Comprueba la dominancia diagonal; si falta, intenta reordenar las ecuaciones.',
        r'Despeja \(x_i\) de la ecuación \(i\) y parte de un vector inicial (por ejemplo, ceros).',
        r'Jacobi: calcula todas las \(x_i^{(k+1)}\) con los valores de la iteración \(k\). Gauss-Seidel: usa los valores ya actualizados.',
        r'Mide el paso \(\lVert x^{(k+1)}-x^{(k)}\rVert_\infty\) y el residuo \(\lVert b-Ax\rVert_\infty\).',
        'Detente cuando el paso sea menor que la tolerancia o se alcance el máximo de iteraciones.',
    ],
    'example': {
        'title': 'Jacobi sobre el caso base',
        'statement': 'Mismo sistema del módulo, desde x⁽⁰⁾ = (0, 0, 0) y tolerancia 10⁻⁶. Compáralo con Gauss-Seidel (8 iteraciones).',
        'setup_tex': _BASE_TEX,
        'steps': [
            ('Dominancia diagonal.', '4 > 1 + 1, 5 > 1 + 1 y 6 > 1 + 1: es estricta, así que Jacobi y Gauss-Seidel convergen.'),
            ('Primera iteración.', 'Todas usan x⁽⁰⁾ = 0: x₁ = 9/4 = 2.25; x₂ = 14/5 = 2.8; x₃ = 21/6 = 3.5.'),
            ('Segunda iteración.', 'x₁ = (9 − 2.8 − 3.5)/4 = 0.675; x₂ = (14 − 2.25 − 3.5)/5 = 1.65; x₃ = (21 − 2.25 − 2.8)/6 = 2.658333.'),
            ('Hasta la tolerancia.', 'Los valores oscilan alrededor de (1, 2, 3) y el paso baja a 10⁻⁶ en la iteración 18.'),
        ],
        'columns': ['k', 'x₁', 'x₂', 'x₃', 'Paso ‖Δx‖∞', 'Residuo ‖r‖∞'],
        'rows': [['0', '0.000000', '0.000000', '0.000000', '—', '21.000000'],
                 ['1', '2.250000', '2.800000', '3.500000', '3.500000', '6.300000'],
                 ['2', '0.675000', '1.650000', '2.658333', '1.575000', '2.725000'],
                 ['3', '1.172917', '2.133333', '3.112500', '0.497917', '0.981250'],
                 ['4', '0.938542', '1.942917', '2.948958', '0.234375', '0.424792']],
        'conclusion': 'Jacobi necesita 18 iteraciones donde Gauss-Seidel usa 8: aprovechar los valores recién calculados acelera la convergencia.',
    },
    'pitfalls': [
        ('¿Sin dominancia diagonal el método diverge?', 'No necesariamente: la dominancia es suficiente, no necesaria. Pero sin ella no hay garantía.'),
        ('¿Jacobi tiene alguna ventaja?', 'Sí: cada incógnita se calcula de forma independiente, así que se paraleliza fácilmente.'),
        ('¿Qué valor de λ elegir?', 'Depende del problema. Para sistemas que provienen de ecuaciones de Laplace suele estar entre 1.2 y 1.8; se ajusta por prueba.'),
    ],
    'lab': {'kind': 'iterative', 'title': 'Jacobi contra Gauss-Seidel',
            'intro': 'Compara cómo baja el residuo con cada método. Prueba cambiar el orden de las filas o el factor de relajación.'},
    'quiz': [
        {'q': 'La diferencia entre Jacobi y Gauss-Seidel es que Gauss-Seidel…',
         'options': ['Usa pivoteo parcial', 'Usa los valores nuevos en cuanto los calcula', 'No necesita valor inicial', 'Es un método directo'],
         'answer': 1, 'why': 'Jacobi usa solo valores de la iteración anterior; Gauss-Seidel aprovecha los ya actualizados.'},
        {'q': 'Un sistema tridiagonal de 1000 ecuaciones se resuelve mejor con…',
         'options': ['Gauss-Jordan', 'La inversa de A', 'El algoritmo de Thomas', 'La regla de Cramer'],
         'answer': 2, 'why': 'Thomas aprovecha la estructura de banda: su costo crece linealmente con n.'},
    ],
}

LESSONS = [GAUSS_JORDAN, LU, JACOBI]
