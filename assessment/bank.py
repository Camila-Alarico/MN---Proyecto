"""Banco de preguntas de evaluación, ligado a los temas reales de los módulos de NumLearn.

Cada pregunta indica `topic` (slug real del tema) y se muestra con su fuente (`SOURCES`: nombre de la
plantilla y URL de la lección). Hay tres formatos, pensados para que copiar el enunciado en una IA no baste:

  multi  Selección múltiple: 5 o 6 opciones y VARIAS correctas (no se revela cuántas).
  open   Respuesta abierta: texto libre que debe explicar, justificar o describir un procedimiento.
         Se corrige con una rúbrica de conceptos y se valora con una rúbrica de conceptos.
  steps  Problema paso a paso: datos distintos en cada intento; no se avanza sin completar el paso anterior.
"""
import random

from . import generators as gen
from .generators import n

SOURCES = {
    'errores': ('Errores numéricos', '/ecuaciones-no-lineales/errores/', 'templates/nonlinear/errores.html'),
    'conceptos': ('Raíces de ecuaciones', '/ecuaciones-no-lineales/conceptos/', 'templates/nonlinear/conceptos.html'),
    'biseccion': ('Bisección', '/ecuaciones-no-lineales/biseccion/', 'templates/nonlinear/simulator.html'),
    'regla-falsa': ('Regla falsa', '/ecuaciones-no-lineales/regla-falsa/', 'templates/nonlinear/simulator.html'),
    'punto-fijo': ('Punto fijo', '/ecuaciones-no-lineales/punto-fijo/', 'templates/nonlinear/simulator.html'),
    'newton': ('Newton-Raphson', '/ecuaciones-no-lineales/newton/', 'templates/nonlinear/simulator.html'),
    'secante': ('Secante', '/ecuaciones-no-lineales/secante/', 'templates/nonlinear/simulator.html'),
    'raices-multiples': ('Raíces múltiples de polinomios', '/ecuaciones-no-lineales/polinomios/', 'templates/nonlinear/polinomios.html'),
    'formulacion': ('Formulación del sistema A·x = b', '/sistemas-lineales/formulacion/', 'templates/linear/formulacion.html'),
    'eliminacion-gaussiana': ('Eliminación gaussiana', '/sistemas-lineales/eliminacion-gaussiana/', 'templates/linear/simulator.html'),
    'gauss-seidel': ('Gauss-Seidel', '/sistemas-lineales/gauss-seidel/', 'templates/linear/simulator.html'),
    'comparacion-metodos': ('Comparación de métodos', '/sistemas-lineales/comparacion-metodos/', 'templates/linear/comparacion-metodos.html'),
}
MODULE_1 = ('errores', 'conceptos', 'biseccion', 'regla-falsa', 'punto-fijo', 'newton', 'secante', 'raices-multiples')
MODULE_2 = ('formulacion', 'eliminacion-gaussiana', 'gauss-seidel', 'comparacion-metodos')


SUBTOPICS = {  # el banco de errores se organiza por subtemas dentro del tema «errores»
    'medidas': 'Medidas del error',
    'origen': 'Origen y propagación',
    'tolerancia': 'Tolerancia y decisión',
    'escala': 'Escala y referencia cero',
    'representacion': 'Cifras y presentación',
}
_SUB = {  # subtema de las preguntas de errores que ya existían
    'E-m1': 'medidas', 'E-m2': 'escala', 'E-m3': 'origen', 'E-m4': 'tolerancia', 'E-m5': 'origen',
    'E-o1': 'escala', 'E-o2': 'representacion', 'E-o3': 'tolerancia',
    'E-s1': 'medidas', 'E-s2': 'origen', 'E-s3': 'escala',
}


def multi(key, topic, prompt, options, explanation, sub=None):
    """`options`: lista de (texto, es_correcta). Se exige que haya varias correctas y al menos una incorrecta."""
    return {'id': key, 'type': 'multi', 'topic': topic, 'sub': sub or _SUB.get(key), 'prompt': prompt, 'options': [t for t, _ in options],
            'correct': frozenset(i for i, (_, ok) in enumerate(options) if ok), 'explanation': explanation}


def opened(key, topic, prompt, rubric, model, min_words=15, case=None, sub=None):
    """`rubric`: [(concepto, [patrones sin tildes])]. `case(rng)` opcional: devuelve {'prompt', 'must'} con datos propios."""
    return {'id': key, 'type': 'open', 'topic': topic, 'sub': sub or _SUB.get(key), 'prompt': prompt, 'rubric': rubric, 'model': model,
            'min_words': min_words, 'case': case}


def steps(key, topic, title, generator, sub=None):
    return {'id': key, 'type': 'steps', 'topic': topic, 'sub': sub or _SUB.get(key), 'prompt': title, 'generator': generator}


def _error_case(rng):
    v = rng.choice([40, 50, 80, 125, 200])
    approx = round(v * (1 + rng.choice([-1, 1]) * rng.choice([1, 2, 2.5, 4]) / 100), 6)
    ea = abs(v - approx)
    tau = round(ea * rng.choice([0.8, 1.25]), 6)
    return {'prompt': (f'Un sensor mide {n(approx)} cuando el valor de referencia es {n(v)}; la tolerancia absoluta es {n(tau)}. '
                       'Explica con tus palabras, paso a paso, cómo decides si la medición cumple, y escribe el valor de Ea que obtienes.'),
            'must': [ea]}


def _relative_tolerance_case(rng):
    v = rng.choice([50, 80, 125, 200])
    pct = rng.choice([1, 2, 4])
    approx = round(v * (1 - pct / 100), 6)
    limit = rng.choice([pct * 0.8, pct * 1.25])
    return {'prompt': (f'Una pieza debía medir {n(v)} mm y mide {n(approx)} mm. La especificación admite una tolerancia relativa de {n(limit)} %. '
                       'Explica con tus palabras qué calculas y cómo decides si cumple; escribe el valor del error porcentual que obtienes.'),
            'must': [float(pct)]}


def _scale_case(rng):
    ea = rng.choice([0.5, 1, 2])
    small, large = rng.choice([5, 10, 20]), rng.choice([500, 1000, 2000])
    return {'prompt': (f'Dos mediciones tienen el mismo error absoluto de {n(ea)}: la medición A tiene referencia {n(small)} y la B tiene referencia {n(large)}. '
                       'Explica cuál es de peor calidad y por qué, y escribe el error relativo de la medición A como proporción.'),
            'must': [ea / small]}


MULTI = [
    multi('E-m1', 'errores', '¿Cuáles de estas afirmaciones sobre las medidas de error son verdaderas?', [
        ('El error absoluto conserva las unidades de la referencia', True),
        ('El error relativo se obtiene dividiendo el absoluto entre |v|', True),
        ('El error porcentual es 100 veces el error relativo', True),
        ('El error relativo se mide en las mismas unidades que v', False),
        ('El error absoluto puede salir negativo', False),
        ('El error relativo siempre está definido, incluso con v = 0', False)],
        'Ea = |v − ṽ| (unidades de v, nunca negativo); Er = Ea/|v| (sin unidades; no definido si v = 0); Ep = 100·Er.'),
    multi('E-m2', 'errores', 'La referencia vale 0 y la aproximación 0.001. ¿Qué es correcto?', [
        ('Ea = 0.001 sigue siendo una distancia válida', True),
        ('Er y Ep no están definidos, porque habría que dividir entre cero', True),
        ('Se puede comparar Ea con una tolerancia absoluta', True),
        ('Er = 0', False),
        ('Er = 0.001', False),
        ('La aproximación es exacta', False)],
        'La distancia absoluta no divide entre nada; el relativo y el porcentual sí. «No definido» no equivale a «cero».'),
    multi('E-m3', 'errores', '¿Cuáles describen el ORIGEN de un error y no una medida del mismo?', [
        ('Redondeo', True),
        ('Truncamiento', True),
        ('Propagación de los errores de los datos', True),
        ('Error absoluto', False),
        ('Error relativo', False),
        ('Error porcentual', False)],
        'Redondeo, truncamiento y propagación explican de dónde viene una diferencia; absoluto, relativo y porcentual la cuantifican.'),
    multi('E-m4', 'errores', 'Con Ea = 0.05 y tolerancia τ = 0.05 (regla Ea ≤ τ), ¿qué es cierto?', [
        ('La medición cumple la tolerancia', True),
        ('La igualdad está incluida en la regla Ea ≤ τ', True),
        ('No cumple, porque Ea no es estrictamente menor que τ', False),
        ('Depende de si la referencia es positiva o negativa', False),
        ('Hay que convertir ambos valores a porcentaje antes de comparar', False)],
        'La regla declarada usa ≤, así que estar justo en el límite cumple. El signo de la referencia no interviene en Ea.'),
    multi('E-m5', 'errores', 'Al pasar 2.7186 a tres decimales, ¿qué es correcto?', [
        ('El truncado es 2.718', True),
        ('El redondeado es 2.719', True),
        ('Truncar descarta las cifras sobrantes sin considerarlas', True),
        ('Ambos métodos dan 2.719', False),
        ('Ambos métodos dan 2.718', False),
        ('Redondear siempre produce un valor menor que truncar', False)],
        'Truncar corta (2.718). Redondear mira la cifra descartada (6 ≥ 5) y sube la última (2.719).'),
    multi('C-m1', 'conceptos', 'Para asegurar por cambio de signo que f tiene una raíz en [a, b] se necesita…', [
        ('Que f sea continua en [a, b]', True),
        ('Que f(a) y f(b) tengan signos opuestos', True),
        ('Que f sea derivable en todo punto', False),
        ('Que f sea creciente', False),
        ('Que f(a) = −f(b) exactamente', False),
        ('Conocer la derivada de f', False)],
        'El teorema del valor intermedio pide continuidad y signos opuestos; ni la derivabilidad ni la monotonía son necesarias.'),
    multi('C-m2', 'conceptos', 'Sobre el residuo |f(x)| de una aproximación x…', [
        ('Es una señal útil pero no prueba por sí solo que x esté cerca de la raíz', True),
        ('El error real es |x − r| y exige conocer r o una cota', True),
        ('En una función muy plana puede ser pequeño lejos de la raíz', True),
        ('Garantiza siempre que |x − r| es menor que el residuo', False),
        ('Significa que x es exactamente una raíz', False),
        ('Solo se calcula en bisección', False)],
        'Residuo y error son cantidades distintas: una pendiente pequeña hace que |f(x)| sea pequeño aunque x esté lejos.'),
    multi('B-m1', 'biseccion', '¿Qué es verdadero en el método de bisección?', [
        ('El primer punto es (a + b)/2', True),
        ('La longitud del intervalo se reduce a la mitad en cada paso', True),
        ('Se conserva el subintervalo donde hay cambio de signo', True),
        ('Necesita la derivada de f', False),
        ('Un extremo suele quedar fijo muchas iteraciones', False),
        ('El nuevo punto lo decide la recta que une los extremos', False)],
        'Bisección parte siempre por el punto medio. Que un extremo quede retenido y usar la recta es propio de la regla falsa.'),
    multi('B-m2', 'biseccion', 'Si f(a) y f(b) tienen el MISMO signo, ¿qué es correcto?', [
        ('Falta la garantía de raíz por cambio de signo', True),
        ('Puede haber una raíz de multiplicidad par o varias raíces dentro', True),
        ('Conviene mirar la gráfica y elegir otro intervalo', True),
        ('Se demuestra que no existe ninguna raíz', False),
        ('La raíz es el punto medio', False),
        ('Bisección converge igualmente con garantía', False)],
        'El criterio no se cumple, pero eso no demuestra que no haya raíces: una raíz doble toca el eje sin cambiar de signo.'),
    multi('F-m1', 'regla-falsa', '¿Cuáles describen la regla falsa?', [
        ('El nuevo punto es el corte con el eje x de la recta que une los extremos', True),
        ('Conserva el subintervalo con cambio de signo', True),
        ('Un extremo puede quedar retenido y la convergencia volverse lenta', True),
        ('Siempre usa el punto medio', False),
        ('(b − a)/2 es una cota válida del error de cualquier punto', False),
        ('Requiere la derivada de f', False)],
        'Es un método cerrado como bisección, pero el punto interior sale de la recta; por eso (b − a)/2 no acota su error.'),
    multi('P-m1', 'punto-fijo', 'Sobre el método de punto fijo xₙ₊₁ = g(xₙ)…', [
        ('Un punto fijo p cumple g(p) = p', True),
        ('|g′| < 1 cerca del punto es una orientación local de convergencia', True),
        ('g debe ser equivalente al problema original f(x) = 0', True),
        ('Toda g equivalente a f(x) = 0 converge', False),
        ('El residuo se mide como |g(x)|', False),
        ('El resultado no depende del punto inicial', False)],
        'Se busca g(x) = x. La equivalencia conserva soluciones pero no garantiza que la iteración las atraiga.'),
    multi('P-m2', 'punto-fijo', 'Para justificar la convergencia por contracción en [a, b] se comprueba que…', [
        ('g lleva el intervalo [a, b] en sí mismo', True),
        ('|g′(x)| ≤ q < 1 en todo el intervalo', True),
        ('entonces existe un único punto fijo en [a, b]', True),
        ('basta con que g sea continua', False),
        ('g(a) = a y g(b) = b', False),
        ('basta evaluar g en un solo punto', False)],
        'Las dos condiciones (autoaplicación y constante de contracción q < 1) son suficientes; la continuidad sola no lo es.'),
    multi('N-m1', 'newton', '¿Qué puede fallar en Newton-Raphson?', [
        ('Si f′(xₙ) = 0 el paso no está definido', True),
        ('Con un mal punto inicial puede oscilar o divergir', True),
        ('Cerca de una raíz múltiple pierde su velocidad habitual', True),
        ('Siempre converge si existe una raíz', False),
        ('Necesita un intervalo con cambio de signo', False),
        ('No usa la derivada', False)],
        'Newton usa xₙ₊₁ = xₙ − f/f′: divide entre la derivada y depende del punto inicial.'),
    multi('N-m2', 'newton', '¿Qué datos intervienen en un paso de Newton-Raphson?', [
        ('f(xₙ)', True),
        ('f′(xₙ)', True),
        ('Un punto inicial x₀', True),
        ('Dos extremos [a, b]', False),
        ('La integral de f', False),
        ('La segunda derivada, siempre', False)],
        'Un solo punto, el valor de la función y el de su derivada en él. Los extremos son de los métodos cerrados.'),
    multi('S-m1', 'secante', '¿Qué es cierto de la secante?', [
        ('Usa dos aproximaciones anteriores', True),
        ('No necesita la derivada analítica', True),
        ('Falla si f(x₁) = f(x₀)', True),
        ('Mantiene siempre un intervalo con cambio de signo', False),
        ('Usa la segunda derivada', False),
        ('Es idéntica a bisección', False)],
        'La recta por dos puntos reemplaza a la tangente; si las imágenes coinciden, la recta es horizontal y el denominador se anula.'),
    multi('M-m1', 'raices-multiples', 'En f(x) = (x − 1)²(x + 2), sobre la raíz x = 1…', [
        ('Toca el eje sin cambiar de signo', True),
        ('Cumple f(1) = 0 y f′(1) = 0', True),
        ('Buscar solo cambios de signo puede hacer que se omita', True),
        ('f cambia de signo en x = 1', False),
        ('Newton ordinario conserva su convergencia cuadrática', False),
        ('Tiene multiplicidad 1', False)],
        'El factor (x − 1) está al cuadrado: multiplicidad 2, contacto con el eje y derivada nula en la raíz.'),
    multi('M-m2', 'raices-multiples', 'La variante para raíces múltiples xₙ₊₁ = xₙ − f·f′/(f′² − f·f″)…', [
        ('Usa f, f′ y f″', True),
        ('Exige comprobar que el denominador no se anule', True),
        ('Busca recuperar la velocidad que Newton ordinario pierde', True),
        ('Usa solo el punto medio del intervalo', False),
        ('Necesita dos extremos con signos opuestos', False),
        ('No requiere ninguna derivada', False)],
        'Es Newton aplicado a f/f′; por eso involucra la segunda derivada y puede fallar si el denominador es cero.'),
    multi('G-m1', 'eliminacion-gaussiana', '¿Qué hace el pivoteo parcial en la eliminación gaussiana?', [
        ('En cada columna elige el mayor |a_ik| entre las filas k…n', True),
        ('Intercambia filas cuando hace falta', True),
        ('Reduce multiplicadores grandes y el error de redondeo', True),
        ('Intercambia columnas y cambia el orden de las incógnitas', False),
        ('Solo se usa en Gauss-Seidel', False),
        ('Cambia la solución del sistema', False)],
        'Permutar filas no altera la solución; solo evita dividir entre pivotes pequeños, que amplifican el redondeo.'),
    multi('G-m2', 'eliminacion-gaussiana', 'Un pivote casi nulo (|pivote| < ε·máx|a_ij|) indica…', [
        ('Un sistema singular o casi singular', True),
        ('Que la solución puede no ser única o ser inestable', True),
        ('Que conviene avisar en lugar de dar una solución sin reservas', True),
        ('Que x = 0 es la solución', False),
        ('Que el residuo es cero', False),
        ('Que la convergencia está asegurada', False)],
        'La eliminación necesita dividir entre el pivote; si es casi cero el sistema no tiene solución única estable.'),
    multi('G-m3', 'eliminacion-gaussiana', 'Sobre el residuo r = b − A·x de un sistema…', [
        ('r = 0 significa que x satisface todas las ecuaciones (en aritmética exacta)', True),
        ('Una norma ‖r‖∞ pequeña indica que las ecuaciones casi se cumplen', True),
        ('Se calcula sustituyendo la solución en cada ecuación', True),
        ('Es igual al error x − x*', False),
        ('Solo se calcula en métodos directos', False),
        ('No depende de b', False)],
        'El residuo mide cuánto falla cada ecuación; no es el error en x, que requeriría conocer la solución exacta.'),
    multi('D-m1', 'gauss-seidel', '¿Qué es cierto de Gauss-Seidel?', [
        ('Parte de un vector inicial (aquí, el vector cero)', True),
        ('Usa dentro de la misma iteración los valores recién actualizados', True),
        ('Una diagonal nula impide despejar la incógnita', True),
        ('Termina siempre en un número finito de pasos', False),
        ('No necesita criterio de parada', False),
        ('Converge para cualquier matriz', False)],
        'Es iterativo: despeja cada xᵢ con los valores más recientes y se detiene por tolerancia o máximo de iteraciones.'),
    multi('D-m2', 'gauss-seidel', 'La dominancia diagonal estricta por filas, |a_ii| > Σ|a_ij|…', [
        ('Es una condición suficiente de convergencia', True),
        ('No es necesaria: puede converger sin cumplirse', True),
        ('Se comprueba fila por fila antes de iterar', True),
        ('Es necesaria para que exista solución', False),
        ('Garantiza que la solución es x = 0', False),
        ('Implica que la matriz es singular', False)],
        'Suficiente, no necesaria. Si no se cumple no se puede garantizar la convergencia, pero tampoco descartarla.'),
    multi('L-m1', 'formulacion', 'En el sistema A·x = b con A de 3×3…', [
        ('Hay 3 ecuaciones y 3 incógnitas', True),
        ('Cada fila de A son los coeficientes de una ecuación', True),
        ('b recoge los valores observados de cada ecuación', True),
        ('x es un dato conocido de partida', False),
        ('El número de incógnitas no está relacionado con el tamaño de A', False),
        ('Solo importa la primera fila de A', False)],
        'A y b son datos; x es lo que se busca. El tamaño n fija el número de ecuaciones y de incógnitas.'),
    multi('L-m2', 'comparacion-metodos', 'Al comparar eliminación gaussiana y Gauss-Seidel…', [
        ('La eliminación entrega la solución tras un número finito de pasos', True),
        ('Gauss-Seidel produce aproximaciones sucesivas', True),
        ('Se pueden contrastar por residuo y por la diferencia entre sus soluciones', True),
        ('Gauss-Seidel es siempre más rápido', False),
        ('La eliminación nunca necesita pivoteo', False),
        ('Ambas exigen dominancia diagonal', False)],
        'Directo vs. iterativo: pasos finitos frente a convergencia condicionada. Ninguno es mejor en todos los casos.'),

    multi('E-m6', 'errores', 'Si la aproximación está POR ENCIMA de la referencia, ¿qué es correcto sobre el error absoluto?', [
        ('Se obtiene igual con |v − ṽ| que con |ṽ − v|', True),
        ('Su valor no lleva signo negativo', True),
        ('Representa la distancia entre ambos valores', True),
        ('Sale negativo cuando ṽ > v', False),
        ('Debe restarse siempre la aproximación a la referencia sin valor absoluto', False),
        ('Conserva el signo para indicar si se pasó o se quedó corto', False)],
        'El error absoluto es una distancia: el valor absoluto elimina el signo, de modo que ṽ > v y ṽ < v producen la misma medida.', sub='medidas'),
    multi('E-m7', 'errores', 'Un error absoluto de 2 cm se expresa también como 0.02 m. ¿Qué es cierto al cambiar de unidades?', [
        ('El error absoluto cambia de número porque conserva las unidades', True),
        ('El error relativo no cambia si referencia y error usan la misma unidad', True),
        ('El error porcentual no depende de la unidad elegida', True),
        ('El error relativo se multiplica por 100 al pasar de cm a m', False),
        ('El error absoluto no tiene unidades', False),
        ('El porcentaje cambia si se mide en metros en lugar de centímetros', False)],
        'Ea hereda las unidades de la referencia; Er y Ep son cocientes sin unidades y por eso no cambian con la unidad elegida.', sub='medidas'),
    multi('E-m8', 'errores', 'Con v = 80 y ṽ = 79.2, el error absoluto es 0.8. ¿Cuáles afirmaciones son correctas?', [
        ('El error relativo es 0.01', True),
        ('El error porcentual es 1 %', True),
        ('El relativo se calcula dividiendo entre |v|, no entre ṽ', True),
        ('El error relativo es 0.8', False),
        ('El error porcentual es 0.01 %', False),
        ('El error relativo se obtiene dividiendo entre la tolerancia', False)],
        'Er = 0.8/80 = 0.01 y Ep = 100 · 0.01 = 1 %. El denominador es la referencia.', sub='medidas'),
    multi('E-m9', 'errores', '¿Cómo se interpreta un error porcentual de 2.5 %?', [
        ('Por cada 100 unidades de referencia, la aproximación se desvía unas 2.5', True),
        ('Equivale a un error relativo de 0.025', True),
        ('Permite comparar con mediciones de otra escala', True),
        ('Que la aproximación vale 2.5 unidades', False),
        ('Que el error absoluto es 2.5 en cualquier unidad', False),
        ('Que se cumple automáticamente cualquier tolerancia absoluta', False)],
        'El porcentaje expresa la proporción del error respecto a la referencia; por sí solo no indica el error absoluto ni cumple una tolerancia.', sub='medidas'),
    multi('E-m10', 'errores', 'Al restar dos cantidades casi iguales (por ejemplo 100.4 − 100.0)…', [
        ('El resultado es pequeño comparado con los datos', True),
        ('El error absoluto de la diferencia puede ser comparable al de los datos', True),
        ('El error relativo del resultado puede crecer mucho', True),
        ('El error relativo del resultado siempre disminuye', False),
        ('Los errores de los datos se cancelan siempre', False),
        ('El resultado es exacto si los datos tienen muchos decimales', False)],
        'Los errores absolutos se acumulan (hasta sumarse) mientras el resultado se hace pequeño: el error relativo se amplifica.', sub='origen'),
    multi('E-m11', 'errores', 'Cortar una serie infinita después de algunos términos produce un error que…', [
        ('Se llama de truncamiento', True),
        ('Disminuye, en general, al conservar más términos', True),
        ('Es distinto de limitar los decimales que se muestran', True),
        ('Se debe a que la computadora redondea cada operación', False),
        ('No existe si los datos son exactos', False),
        ('Es siempre cero en la práctica', False)],
        'El truncamiento nace del método (proceso infinito sustituido por uno finito), aunque los datos sean exactos.', sub='origen'),
    multi('E-m12', 'errores', 'La computadora guarda 1/3 como 0.333333… con una cantidad finita de cifras. ¿Qué se concluye?', [
        ('Se introduce un error de redondeo', True),
        ('Con más operaciones, esa diferencia puede acumularse', True),
        ('La diferencia con 1/3 es pequeña pero no nula', True),
        ('1/3 se representa exactamente', False),
        ('El error de redondeo nace de cortar una serie', False),
        ('Solo ocurre al imprimir en pantalla', False)],
        'Una representación finita de un número con infinitas cifras introduce redondeo; en cadenas de cálculo puede crecer.', sub='origen'),
    multi('E-m13', 'errores', 'Dos métodos distintos dan 3.14 y 3.1416 para π. ¿Qué conviene afirmar?', [
        ('Hay que compararlos con la referencia mediante un error', True),
        ('Cuál sirve depende de la tolerancia exigida', True),
        ('Mostrar más decimales no basta para concluir mejor exactitud', True),
        ('3.1416 es siempre exacto porque tiene más decimales', False),
        ('3.14 es mejor porque es más corto', False),
        ('Los dos tienen error cero respecto a π', False)],
        'La calidad se mide con el error respecto a la referencia y se juzga con la tolerancia; la longitud del número no la determina.', sub='origen'),
    multi('E-m14', 'errores', '¿Qué diferencia hay entre error y tolerancia?', [
        ('El error mide el resultado obtenido', True),
        ('La tolerancia es el umbral elegido para aceptarlo', True),
        ('Un resultado cumple si su error no supera la tolerancia declarada', True),
        ('Son dos nombres para la misma cantidad', False),
        ('La tolerancia se calcula restando referencia y aproximación', False),
        ('El error es el límite máximo permitido', False)],
        'El error se calcula; la tolerancia se decide. Se comparan para aceptar o rechazar.', sub='tolerancia'),
    multi('E-m15', 'errores', 'Una tolerancia relativa del 2 % para una referencia de 50…', [
        ('Equivale a una tolerancia absoluta de 1', True),
        ('Se compara con el error porcentual', True),
        ('Puede convertirse en absoluta multiplicando por |v|', True),
        ('Equivale a una tolerancia absoluta de 100', False),
        ('Se compara directamente con el error absoluto sin convertir', False),
        ('No depende de la referencia', False)],
        'τ = |v| · 2/100 = 1. Una tolerancia relativa solo tiene sentido con una referencia concreta.', sub='tolerancia'),
    multi('E-m16', 'errores', 'Si no se conoce la raíz verdadera, en un algoritmo iterativo se controlan el cambio entre pasos, el residuo o una cota. ¿Qué es correcto?', [
        ('Ninguno de ellos debe presentarse automáticamente como error real', True),
        ('La cota de bisección sí acota el error de su punto medio', True),
        ('Un residuo pequeño puede coexistir con un error grande si la función es plana', True),
        ('El cambio entre pasos es siempre el error real', False),
        ('El residuo es el error absoluto de la raíz', False),
        ('Los tres valores coinciden siempre', False)],
        'Son indicadores para decidir cuándo parar; sin la raíz verdadera no se conoce el error real, y los indicadores pueden diferir.', sub='tolerancia'),
    multi('E-m17', 'errores', 'Dos mediciones tienen el mismo error absoluto de 1, una sobre 10 y otra sobre 1000. ¿Qué es cierto?', [
        ('La primera tiene un error relativo mucho mayor', True),
        ('La segunda es mejor en proporción', True),
        ('El error absoluto solo no basta para compararlas', True),
        ('Las dos tienen la misma calidad porque Ea es igual', False),
        ('La segunda tiene un error relativo 100 veces mayor', False),
        ('Los errores relativos son iguales a los absolutos', False)],
        'Er = 1/10 = 0.1 frente a Er = 1/1000 = 0.001: la misma distancia pesa mucho más sobre una referencia pequeña.', sub='escala'),
    multi('E-m18', 'errores', 'Con referencia v = 0, ¿qué puede hacerse?', [
        ('Calcular el error absoluto', True),
        ('Compararlo con una tolerancia absoluta', True),
        ('Afirmar que el error relativo no está definido', True),
        ('Calcular Er dividiendo entre cero y obtener cero', False),
        ('Decir que el error porcentual vale 0 %', False),
        ('Usar el error relativo como única medida de calidad', False)],
        'Ea y la comparación absoluta siguen siendo válidos; Er y Ep dividen entre |v| = 0 y no están definidos.', sub='escala'),
    multi('E-m19', 'errores', 'Para decidir cuál de dos instrumentos es más preciso en proporción a lo que mide, conviene…', [
        ('Comparar sus errores relativos', True),
        ('Calcular cada Er como Ea/|v|', True),
        ('Fijarse en que un Ea mayor puede ser menor en proporción', True),
        ('Elegir el que tenga menor error absoluto sin mirar la escala', False),
        ('Comparar solo las referencias', False),
        ('Sumar ambos errores absolutos', False)],
        'El criterio proporcional es el error relativo; con referencias muy distintas el error absoluto engaña.', sub='escala'),
    multi('E-m20', 'errores', '¿Más decimales mostrados significan más exactitud?', [
        ('No: 9.8000000000 y 9.8 son el mismo valor', True),
        ('La distancia a la referencia no cambia al agregar ceros', True),
        ('Las cifras mostradas se interpretan a partir del error', True),
        ('Sí, porque el número queda más largo', False),
        ('Sí, agregar decimales acerca el valor a la referencia', False),
        ('Solo importa la cantidad de decimales, no el error', False)],
        'Mostrar más ceros solo cambia la presentación: la exactitud la da la distancia a la referencia.', sub='representacion'),
    multi('E-m21', 'errores', 'El control «decimales mostrados» del Explorador de errores…', [
        ('Cambia solo la presentación', True),
        ('No altera la precisión interna', True),
        ('No cambia el error calculado', True),
        ('Redondea los datos antes de calcular el error', False),
        ('Modifica la tolerancia', False),
        ('Convierte el truncamiento en redondeo', False)],
        'Ocultar o mostrar decimales es una operación de presentación distinta del redondeo y del truncamiento.', sub='representacion'),
    multi('E-m22', 'errores', 'Respecto a redondear y truncar un número a k decimales…', [
        ('Redondear elige el número más cercano con las cifras permitidas', True),
        ('Truncar descarta las cifras sobrantes', True),
        ('Ambos pueden dar el mismo valor cuando la primera cifra descartada es menor que 5', True),
        ('Truncar siempre da el valor más cercano', False),
        ('Redondear nunca cambia el último dígito', False),
        ('Truncar y redondear son lo mismo que ocultar decimales', False)],
        'Si la primera cifra descartada es menor que 5, redondear y truncar coinciden; si es 5 o más, redondear sube la última cifra.', sub='representacion'),
    multi('E-m23', 'errores', 'Al redondear a k decimales, la diferencia con el valor original…', [
        ('No supera media unidad de la última cifra conservada', True),
        ('Se acota por 0.5 · 10^(−k)', True),
        ('Es un error de redondeo', True),
        ('Puede ser tan grande como una unidad completa de la última cifra', False),
        ('Es siempre cero', False),
        ('Depende solo del signo del número', False)],
        'Redondeando al más cercano, el error absoluto máximo es 0.5 · 10^(−k).', sub='representacion'),
]

OPEN = [
    opened('E-o1', 'errores', 'Un error absoluto de 0.1 puede ser aceptable en una medición e inaceptable en otra. Explica por qué y di qué medida usarías para compararlas.', [
        ('usa una medida relativa o porcentual', [r'relativ', r'porcentu', r'proporci', r'cociente']),
        ('relaciona el error con el tamaño de la referencia', [r'referencia', r'valor verdadero', r'magnitud', r'escala', r'tamano']),
        ('indica la división (error entre referencia) o la falta de unidades', [r'divid', r'entre', r'sin unidades', r'cociente'])],
        'El error absoluto no dice nada del tamaño de lo medido: 0.1 sobre una referencia de 1 es 10 %, sobre 1000 es 0.01 %. '
        'Por eso se compara con el error relativo (o porcentual), que divide Ea entre |referencia| y no tiene unidades.', 20),
    opened('E-o2', 'errores', 'Un compañero afirma que mostrar 1.500000 en lugar de 1.5 vuelve la aproximación más precisa. ¿Tiene razón? Justifica con la diferencia entre el valor y su presentación.', [
        ('indica que es el mismo valor / no cambia', [r'mismo valor', r'mismo numero', r'igual', r'no cambia', r'no modifica', r'misma cantidad']),
        ('distingue decimales mostrados de la aproximación', [r'decimales', r'presentacion', r'mostrar', r'cifras', r'formato']),
        ('relaciona la precisión con la distancia a la referencia', [r'error', r'referencia', r'distancia', r'acerca', r'valor real'])],
        'No. 1.5 y 1.500000 son el mismo número; agregar ceros cambia la presentación, no la distancia a la referencia. '
        'La aproximación mejora solo si se acerca al valor de referencia.', 18),
    opened('E-o3', 'errores', 'Resuelve un caso con tus propios datos y explica el procedimiento.', [
        ('resta referencia y aproximación / valor absoluto', [r'resta', r'diferencia', r'valor absoluto', r'distancia', r'\|']),
        ('compara con la tolerancia', [r'compar', r'menor', r'mayor', r'<=', r'tolerancia', r'limite']),
        ('concluye si cumple o no', [r'cumple', r'no cumple', r'acept', r'rechaz', r'dentro', r'fuera'])],
        'Ea = |v − ṽ|; se compara Ea con τ (cumple si Ea ≤ τ) y se concluye.', 18, case=_error_case),
    opened('C-o1', 'conceptos', '¿Por qué encontrar un x con f(x) casi cero no garantiza que x esté cerca de la raíz? Menciona un tipo de función donde ocurre.', [
        ('distingue residuo |f(x)| de error |x − r|', [r'residuo', r'valor de la funcion', r'f\(x\)', r'error real', r'distancia a la raiz']),
        ('habla de funciones planas / pendiente pequeña', [r'plana', r'pendiente', r'derivada (muy )?peque', r'casi horizontal', r'aplan']),
        ('indica que x puede estar lejos de la raíz', [r'lejos', r'alejad', r'no esta cerca', r'no garantiza'])],
        'El residuo mide qué tan cerca está f(x) de 0, no qué tan cerca está x de r. Si la gráfica es casi horizontal cerca del eje, '
        '|f(x)| es pequeño aunque x esté lejos de la raíz.', 20),
    opened('C-o2', 'conceptos', 'Antes de aplicar bisección en [a, b], ¿qué debes comprobar? Si f(a) y f(b) tienen el mismo signo, ¿qué puedes y qué no puedes concluir?', [
        ('menciona la continuidad', [r'continu']),
        ('pide signos opuestos / cambio de signo', [r'signos? opuestos', r'cambio de signo', r'f\(a\).*f\(b\).*<\s*0']),
        ('aclara que el mismo signo no prueba que no haya raíz', [r'no (se )?(puede|prueba|demuestra|garantiza)', r'multiplicidad', r'raiz doble', r'numero par', r'podria haber'])],
        'Hay que comprobar que f sea continua y que f(a) y f(b) tengan signos opuestos. Con el mismo signo falta la garantía, '
        'pero no se puede afirmar que no existan raíces (por ejemplo, una raíz doble o dos raíces dentro).', 22),
    opened('B-o1', 'biseccion', 'Describe paso a paso una iteración completa de bisección sobre un intervalo [a, b] con cambio de signo.', [
        ('calcula el punto medio', [r'punto medio', r'\(a ?\+ ?b\) ?/ ?2', r'mitad']),
        ('evalúa f en el punto medio y mira el signo', [r'evalu', r'signo', r'f\(m']),
        ('conserva el subintervalo con cambio de signo', [r'conserv', r'subintervalo', r'nuevo intervalo', r'me quedo', r'descart']),
        ('repite hasta cumplir un criterio de parada', [r'repit', r'tolerancia', r'criterio', r'hasta'])],
        'Calculo m = (a + b)/2, evalúo f(m), comparo su signo con f(a) y f(b), conservo el subintervalo donde hay cambio de signo y repito hasta que '
        'la cota de error sea menor que la tolerancia.', 25),
    opened('B-o2', 'biseccion', 'Explica por qué bisección siempre converge pero puede ser lenta. Estima cuántas iteraciones hacen falta para pasar de un intervalo de longitud 1 a menos de 0.001 y justifica tu cuenta.', [
        ('el intervalo se reduce a la mitad', [r'mitad', r'divide', r'reduce', r'/ ?2', r'1/2']),
        ('la convergencia se apoya en el cambio de signo / continuidad', [r'cambio de signo', r'garantiza', r'encierra', r'continu']),
        ('llega a unas 10 iteraciones (2^10 = 1024)', [r'\b10\b', r'\bdiez\b', r'2\^10', r'1024', r'log'])],
        'Cada paso divide la longitud entre 2 y siempre conserva un cambio de signo, por eso converge, pero la reducción es lenta. '
        'Se necesita 1/2ⁿ < 0.001, es decir n ≥ 10 (2¹⁰ = 1024).', 25),
    opened('F-o1', 'regla-falsa', 'Compara regla falsa y bisección: ¿en qué se parecen, en qué se diferencian y por qué en la regla falsa un extremo puede quedar fijo?', [
        ('ambos conservan un intervalo con cambio de signo', [r'cambio de signo', r'encierr', r'intervalo', r'cerrad']),
        ('regla falsa usa la recta / corte; bisección el punto medio', [r'recta', r'corte', r'interpol', r'punto medio', r'secante']),
        ('explica el extremo retenido por la curvatura / lentitud', [r'fij', r'retenid', r'inmovil', r'curvatura', r'lent', r'no se mueve'])],
        'Ambos son métodos cerrados que conservan el cambio de signo. Bisección usa el punto medio; regla falsa usa el corte de la recta entre los extremos. '
        'Si la curva es muy convexa, el corte cae siempre del mismo lado y un extremo queda retenido, lo que vuelve lenta la convergencia.', 25),
    opened('P-o1', 'punto-fijo', 'Antes de iterar con una g(x) para resolver f(x) = 0, ¿qué comprobaciones haces para saber si la iteración tiene sentido y puede converger?', [
        ('g debe ser equivalente al problema y cumplir g(p) = p', [r'equivalen', r'g\(p\) ?= ?p', r'g\(x\) ?= ?x', r'punto fijo']),
        ('revisa |g′| < 1', [r'g\'', r'g′', r'derivada', r'pendiente', r'< ?1', r'menor (que )?1']),
        ('verifica que g lleve el intervalo en sí mismo / contracción', [r'intervalo', r'si mismo', r'contracci', r'autoaplic'])],
        'Verifico que g sea equivalente a f(x) = 0 (los puntos fijos g(p) = p son raíces), que g lleve el intervalo en sí mismo y que |g′(x)| ≤ q < 1 '
        'en él (contracción).', 25),
    opened('N-o1', 'newton', 'Describe cómo se calcula un paso de Newton-Raphson y explica qué ocurre si f′(x₀) = 0.', [
        ('da la fórmula x₁ = x₀ − f/f′ o menciona la tangente', [r'x ?- ?f', r'x0 ?- ?f', r'tangente', r'f\(x[0n₀]?\) ?/ ?f']),
        ('usa f y f′ en el punto actual', [r'derivada', r'f′', r'f\'', r'evalu']),
        ('explica que con f′ = 0 no está definido / división entre cero', [r'divid', r'cero', r'no (esta )?defin', r'indefin', r'cambiar.*inicio', r'otro punto'])],
        'x₁ = x₀ − f(x₀)/f′(x₀): se traza la tangente en x₀ y se toma su corte con el eje. Si f′(x₀) = 0 la tangente es horizontal, '
        'hay división entre cero y el paso no está definido; hay que cambiar el punto inicial.', 22),
    opened('N-o2', 'newton', '¿Por qué Newton puede divergir aunque exista una raíz? Menciona al menos dos causas y cómo lo notarías en la tabla de iteraciones.', [
        ('punto inicial lejano o mal elegido / oscilación', [r'inicial', r'lejan', r'oscil', r'salta', r'lejos']),
        ('derivada pequeña o nula', [r'derivada', r'pendiente', r'f′', r'f\'', r'cero']),
        ('lo detecta en el paso o el residuo que no disminuye / crece', [r'residuo', r'paso', r'crece', r'no disminuye', r'aumenta', r'no se estabiliza'])],
        'Con un punto inicial lejano la tangente puede llevar a otra zona u oscilar, y con derivada casi nula el paso se dispara. '
        'En la tabla el paso y el residuo no disminuyen (o crecen).', 25),
    opened('S-o1', 'secante', 'Compara secante con Newton: ¿qué dato evita la secante, qué usa en su lugar y qué riesgo aparece si f(x₁) = f(x₀)?', [
        ('evita la derivada', [r'derivada', r'f′', r'f\'']),
        ('usa dos aproximaciones / puntos previos', [r'dos (\w+ )?(puntos|aproxim|valores)', r'puntos? (previos|anteriores)', r'x0.*x1', r'recta secante']),
        ('el riesgo es un denominador cero / recta horizontal', [r'denominador', r'cero', r'horizontal', r'divid'])],
        'La secante evita la derivada de Newton y la reemplaza por la pendiente de la recta que pasa por las dos últimas aproximaciones. '
        'Si f(x₁) = f(x₀) la recta es horizontal y el denominador se anula.', 22),
    opened('M-o1', 'raices-multiples', 'Explica por qué cerca de una raíz doble Newton pierde velocidad, qué variante se usa (y qué derivadas necesita) y por qué la gráfica puede engañarnos.', [
        ('la multiplicidad hace que f′ también tienda a cero / convergencia lineal', [r'multiplicidad', r'derivada.*cero', r'lineal', r'lent', r'pierde']),
        ('la variante usa f, f′ y f″', [r'segunda derivada', r'f″', r'f\'\'', r'f ?, ?f.*f', r'modificad']),
        ('la raíz toca el eje sin cruzar / no hay cambio de signo', [r'toca', r'sin cruzar', r'no cruza', r'cambio de signo', r'tangente al eje'])],
        'En una raíz doble f y f′ se anulan, así que el cociente f/f′ pierde precisión y Newton converge solo linealmente. '
        'La variante usa f, f′ y f″. Además, la gráfica toca el eje sin cruzarlo y no hay cambio de signo que la delate.', 28),
    opened('G-o1', 'eliminacion-gaussiana', 'Usando como ejemplo un coeficiente a₁₁ = 0.01 junto a un a₃₃ = 100, explica por qué se hace pivoteo parcial y qué problema numérico se evita.', [
        ('un pivote pequeño produce multiplicadores grandes', [r'multiplicador', r'dividir entre', r'divid.*peque', r'pivote (muy )?peque', r'cercano a cero']),
        ('esto amplifica el error de redondeo', [r'redondeo', r'amplific', r'error', r'inestab', r'pierde.*cifras']),
        ('se elige el mayor valor absoluto / se intercambian filas', [r'mayor', r'valor absoluto', r'intercamb', r'permut', r'mover'])],
        'Dividir entre 0.01 produce multiplicadores enormes (por ejemplo 100/0.01 = 10 000) que amplifican el error de redondeo. '
        'Con pivoteo parcial se intercambian filas para usar como pivote el mayor |a_ik| de la columna.', 25),
    opened('G-o2', 'eliminacion-gaussiana', 'Describe el procedimiento completo para resolver un sistema 3×3 por eliminación gaussiana con pivoteo parcial, desde la matriz aumentada hasta comprobar el resultado.', [
        ('arma la matriz aumentada [A | b]', [r'aumentada', r'\[a ?\| ?b\]', r'a ?\| ?b']),
        ('elige el pivote e intercambia filas', [r'pivote', r'intercamb', r'mayor']),
        ('usa multiplicadores para anular debajo del pivote', [r'multiplicador', r'anul', r'ceros', r'eliminar', r'restar']),
        ('hace sustitución hacia atrás', [r'hacia atras', r'sustituci', r'triangular', r'x3.*x2.*x1']),
        ('comprueba con el residuo b − A·x', [r'residuo', r'sustituy.*ecuacion', r'comprob', r'verific'])],
        'Armo [A | b]; en cada columna elijo como pivote el mayor |a_ik| (intercambio filas), calculo los multiplicadores y anulo lo que está debajo; '
        'con la matriz triangular hago sustitución hacia atrás (x₃, x₂, x₁) y verifico con el residuo r = b − A·x.', 30),
    opened('D-o1', 'gauss-seidel', 'Explica cómo Gauss-Seidel actualiza las incógnitas en una iteración y en qué se diferencia de usar solo los valores de la iteración anterior.', [
        ('despeja cada incógnita de su ecuación', [r'despej', r'cada ecuacion', r'x_?i']),
        ('usa de inmediato los valores recién actualizados', [r'recien', r'inmediat', r'actualizad', r'ya calculad', r'nuevos? valor', r'valores nuevos']),
        ('parte de un vector inicial e itera hasta la tolerancia', [r'inicial', r'itera', r'tolerancia', r'repit', r'vector cero'])],
        'En cada iteración se despeja xᵢ de la ecuación i; al calcular xᵢ se usan ya los valores nuevos de x₁…xᵢ₋₁ y los viejos de las demás. '
        'Se parte de un vector inicial y se repite hasta alcanzar la tolerancia.', 25),
    opened('D-o2', 'gauss-seidel', 'Tienes una matriz que NO es diagonalmente dominante. ¿Puedes asegurar que Gauss-Seidel no convergerá? Justifica y di qué harías.', [
        ('la dominancia es suficiente, no necesaria', [r'suficiente', r'no (es )?necesaria', r'no es obligatoria']),
        ('no se puede asegurar: puede converger o no', [r'puede (converger|que converja)', r'no (se )?(puede|garantiza|asegura)', r'podria']),
        ('propone reordenar filas, usar eliminación o revisar el residuo', [r'reorden', r'intercamb', r'eliminacion', r'directo', r'residuo', r'probar'])],
        'No. La dominancia diagonal es una condición suficiente, no necesaria: sin ella no se garantiza la convergencia, pero puede ocurrir. '
        'Reordenaría las filas, probaría observando el residuo o usaría eliminación gaussiana.', 25),
    opened('L-o1', 'formulacion', 'En el caso A = (4 1 1; 1 5 1; 1 1 6), b = (9, 14, 21) se afirma que x = (1, 2, 3) es la solución. Explica cómo lo comprobarías sin volver a resolver el sistema.', [
        ('sustituye x en cada ecuación / calcula A·x', [r'sustitu', r'a ?· ?x', r'a por x', r'multiplic', r'fila por fila']),
        ('compara el resultado con b', [r'compar', r'igual a b', r'= ?b', r'coincid', r'\b9\b.*\b14\b']),
        ('menciona el residuo cero o que cada ecuación se cumple', [r'residuo', r'cero', r'se cumple', r'cumplen todas'])],
        'Calculo A·x fila por fila: 4·1+1·2+1·3 = 9, 1·1+5·2+1·3 = 14, 1·1+1·2+6·3 = 21. Como coincide con b, el residuo r = b − A·x es cero.', 20),
    opened('L-o2', 'comparacion-metodos', 'Compara eliminación gaussiana y Gauss-Seidel: ¿cuándo preferirías cada una? Apóyate en el residuo, el número de pasos y las condiciones de convergencia.', [
        ('la eliminación es directa: pasos finitos', [r'directo', r'finit', r'numero fijo', r'exact']),
        ('Gauss-Seidel es iterativo y aproxima', [r'iterativ', r'aproxim', r'iteraci', r'sucesiv']),
        ('Gauss-Seidel depende de la convergencia / dominancia', [r'dominan', r'converg', r'condicion']),
        ('se contrastan con residuo o tolerancia', [r'residuo', r'tolerancia', r'error'])],
        'La eliminación es un método directo con un número finito de pasos y sirve para cualquier sistema no singular; Gauss-Seidel es iterativo, '
        'solo converge bajo condiciones como la dominancia diagonal y se detiene por tolerancia. Se comparan con el residuo.', 28),

    opened('E-o4', 'errores', 'Un compañero dice «mi aproximación tiene un error de 2 cm» y concluye que es buena. ¿Qué información falta para juzgarla y qué medida usarías?', [
        ('pide la referencia o la escala de lo medido', [r'referencia', r'escala', r'tamano', r'valor verdadero', r'cuanto mide', r'magnitud']),
        ('propone el error relativo o porcentual', [r'relativ', r'porcentu', r'proporci']),
        ('menciona la tolerancia o el criterio para aceptar', [r'tolerancia', r'umbral', r'limite', r'aceptable', r'criterio'])],
        'Falta saber sobre qué referencia se midió: 2 cm es mucho sobre 10 cm y poco sobre 10 m. Usaría el error relativo o porcentual y lo compararía con la tolerancia.', 20, sub='medidas'),
    opened('E-o5', 'errores', '¿Por qué el error absoluto no puede salir negativo y qué se hace con el signo de la diferencia?', [
        ('lo define como una distancia / magnitud', [r'distancia', r'magnitud', r'cuanto se aleja', r'separaci']),
        ('menciona el valor absoluto', [r'valor absoluto', r'\|']),
        ('indica que la resta puede salir negativa y el signo se descarta', [r'resta', r'diferencia', r'sin signo', r'signo', r'negativ'])],
        'Es una distancia entre dos valores, así que usa el valor absoluto de la resta: la diferencia puede salir negativa, pero el signo se descarta.', 18, sub='medidas'),
    opened('E-o6', 'errores', 'Explica la diferencia entre error de redondeo y error de truncamiento y da un ejemplo de cada uno.', [
        ('el redondeo viene de representar con cifras finitas', [r'cifras finitas', r'representa', r'decimales', r'cantidad finita', r'1/3', r'0\.3333']),
        ('el truncamiento viene de cortar un proceso o serie', [r'serie', r'terminos', r'cortar', r'proceso infinito', r'finito', r'metodo']),
        ('da al menos un ejemplo', [r'por ejemplo', r'ejemplo', r'1/3', r'serie', r'pi', r'2\.71'])],
        'El redondeo nace de guardar números con cifras finitas (1/3 como 0.333333). El truncamiento nace del método: cortar una serie infinita tras pocos términos, por ejemplo aproximar e con tres términos.', 25, sub='origen'),
    opened('E-o7', 'errores', 'Explica por qué restar dos números casi iguales puede amplificar el error relativo. Apóyate en un ejemplo con números.', [
        ('el resultado es pequeño', [r'pequeno', r'poca magnitud', r'casi cero', r'cerca de cero']),
        ('los errores absolutos se suman o se mantienen', [r'error(es)? absoluto', r'se suman', r'se acumul', r'mismo error', r'no se cancel']),
        ('el error relativo crece al dividir entre un valor pequeño', [r'relativ', r'proporci', r'porcentaj', r'amplific', r'crece', r'aumenta'])],
        'Al restar 100.4 − 100.0 queda 0.4, un valor pequeño. Los errores absolutos de los datos se acumulan, y como se dividen entre 0.4, el error relativo del resultado crece mucho respecto al de los datos.', 28, sub='origen'),
    opened('E-o8', 'errores', '¿Por qué mostrar menos decimales en pantalla no es lo mismo que redondear internamente un valor?', [
        ('mostrar es presentación', [r'presentaci', r'visual', r'pantalla', r'solo muestra', r'formato']),
        ('el valor interno y el error no cambian', [r'valor interno', r'no cambia', r'sigue igual', r'precision interna', r'mismo valor', r'no altera']),
        ('el redondeo sí modifica el valor y su error', [r'redondeo', r'modifica', r'cambia el valor', r'introduce error', r'error'])],
        'Mostrar menos decimales solo cambia la presentación: el valor interno y el error calculado siguen igual. Redondear sí sustituye el valor por otro y esa diferencia es un error.', 22, sub='representacion'),
    opened('E-o9', 'errores', 'Un compañero dice «mi error es 0.05, por lo tanto cumple». ¿Qué le falta a esa conclusión?', [
        ('falta compararlo con la tolerancia', [r'tolerancia', r'umbral', r'limite', r'permitid']),
        ('distingue error de tolerancia', [r'error', r'medida', r'resultado', r'obtenid']),
        ('menciona que la tolerancia debe ser del mismo tipo (absoluta/relativa)', [r'mismo tipo', r'absolut', r'relativ', r'misma', r'unidades'])],
        'Falta compararlo con la tolerancia declarada: el error es una medida del resultado y la tolerancia es el umbral. Además deben ser del mismo tipo (absoluta con absoluta, relativa con relativa).', 20, sub='tolerancia'),
    opened('E-o10', 'errores', 'Resuelve un caso con tolerancia relativa y explica el procedimiento.', [
        ('calcula el error absoluto como diferencia', [r'resta', r'diferencia', r'valor absoluto', r'distancia', r'\|']),
        ('lo convierte en porcentaje dividiendo entre la referencia', [r'divid', r'entre', r'cociente', r'porcentu', r'relativ']),
        ('compara con la tolerancia y concluye', [r'compar', r'menor', r'mayor', r'tolerancia', r'cumple'])],
        'Calculo Ea = |v − ṽ|, lo divido entre |v| y lo multiplico por 100 para obtener el error porcentual, y lo comparo con la tolerancia relativa.', 22, case=_relative_tolerance_case, sub='tolerancia'),
    opened('E-o11', 'errores', 'Si la referencia es cero, ¿qué medidas de error se pueden calcular y cuáles no? Justifica.', [
        ('el error absoluto sí se puede calcular', [r'absoluto.*(si|se puede|definid|valid)', r'(si|se puede).*absoluto']),
        ('el relativo y el porcentual no están definidos', [r'relativ', r'porcentu', r'no (esta|estan) definid', r'indefinid']),
        ('porque habría que dividir entre cero', [r'divid.*cero', r'entre cero', r'denominador', r'cero.*divis'])],
        'El error absoluto sí se puede calcular y comparar con una tolerancia absoluta. El relativo y el porcentual no están definidos porque habría que dividir entre |v| = 0; «no definido» no equivale a cero.', 25, sub='escala'),
    opened('E-o12', 'errores', 'Compara dos mediciones con el mismo error absoluto y escribe lo que se pide.', [
        ('compara por el error relativo', [r'relativ', r'proporci', r'porcentu']),
        ('la referencia menor produce el mayor error relativo', [r'referencia (mas )?peque', r'menor referencia', r'valor (mas )?peque', r'escala (mas )?peque', r'a igual']),
        ('concluye cuál es de peor calidad', [r'peor', r'menos precis', r'mayor error', r'es la a', r'la medicion a'])],
        'La medición A, con referencia pequeña, tiene un error relativo mucho mayor que la B aunque Ea sea el mismo, así que es de peor calidad en proporción.', 22, case=_scale_case, sub='escala'),
    opened('E-o13', 'errores', '¿Más decimales significan más exactitud? Argumenta con el ejemplo de mostrar 9.8000000000 en lugar de 9.8 cuando la referencia es 10.', [
        ('responde que no', [r'\bno\b', r'no mejora', r'no significa', r'falso']),
        ('dice que es el mismo valor / misma distancia', [r'mismo valor', r'misma distancia', r'igual', r'no cambia', r'no reduce']),
        ('relaciona la exactitud con el error respecto a la referencia', [r'referencia', r'error', r'distancia', r'10'])],
        'No. 9.8 y 9.8000000000 son el mismo valor y están igual de lejos de 10; agregar ceros cambia la presentación, no la exactitud, que se juzga por el error respecto a la referencia.', 20, sub='representacion'),
    opened('E-o14', 'errores', 'Si no conozco la raíz verdadera, ¿qué cantidades controlo en un algoritmo iterativo y por qué no debo presentarlas como error real?', [
        ('menciona el cambio entre pasos, el residuo o una cota', [r'cambio entre pasos', r'paso', r'residuo', r'cota']),
        ('dice que no son el error real', [r'no (son|es) (el )?error real', r'no es el error', r'no equivale', r'no necesariamente', r'no garantiza']),
        ('explica que el error real exige conocer la raíz', [r'conocer la raiz', r'raiz verdadera', r'valor verdadero', r'desconoc'])],
        'Controlo el cambio entre pasos, el residuo o una cota. No son el error real: este requiere conocer la raíz verdadera, y un paso o residuo pequeño puede coexistir con un error grande.', 25, sub='tolerancia'),
    opened('E-o15', 'errores', 'Describe cómo se origina el error de truncamiento cuando se aproxima e con solo unos términos de su serie.', [
        ('la serie es infinita y se corta', [r'serie', r'infinit', r'cortar', r'corta', r'terminos']),
        ('el error es la parte que se descarta / diferencia con la referencia', [r'descart', r'diferencia', r'faltan', r'restantes', r'error']),
        ('mejora al agregar más términos', [r'mas terminos', r'aumentar', r'disminuy', r'reduce', r'mejora', r'acerca'])],
        'e se define con una serie infinita; al conservar solo unos términos se descarta el resto, y esa parte omitida es el error de truncamiento, que disminuye al agregar más términos.', 22, sub='origen'),
]

STEPS = [
    steps('E-s1', 'errores', 'Medidas de error y decisión con la tolerancia', gen.error_measures),
    steps('E-s2', 'errores', 'Truncamiento frente a redondeo', gen.round_vs_truncate),
    steps('E-s3', 'errores', 'El mismo error absoluto con referencias de distinta escala', gen.same_error_different_scale),
    steps('B-s1', 'biseccion', 'Primera iteración de bisección', gen.bisection_step),
    steps('F-s1', 'regla-falsa', 'Primera iteración de regla falsa', gen.false_position_step),
    steps('P-s1', 'punto-fijo', 'Iteración de punto fijo y criterio de convergencia', gen.fixed_point_step),
    steps('N-s1', 'newton', 'Un paso de Newton-Raphson', gen.newton_step),
    steps('S-s1', 'secante', 'Un paso del método de la secante', gen.secant_step),
    steps('G-s1', 'eliminacion-gaussiana', 'Eliminación con pivoteo parcial en un sistema 2×2', gen.gauss_pivot_2x2),
    steps('G-s2', 'eliminacion-gaussiana', 'Sustitución hacia atrás y residuo en un sistema 3×3', gen.gauss_back_substitution),
    steps('D-s1', 'gauss-seidel', 'Primera iteración de Gauss-Seidel y dominancia diagonal', gen.seidel_step),

    steps('E-s4', 'errores', 'Tolerancia relativa: del porcentaje a la decisión', gen.tolerance_relative, sub='tolerancia'),
    steps('E-s5', 'errores', 'Propagación del error en una suma de tramos', gen.propagation_sum, sub='origen'),
    steps('E-s6', 'errores', 'Restar cantidades casi iguales amplifica el error relativo', gen.cancellation, sub='origen'),
    steps('E-s7', 'errores', 'Referencia igual a cero: qué se puede decidir', gen.reference_zero, sub='escala'),
    steps('E-s8', 'errores', 'Referencia negativa: el error no lleva signo', gen.negative_reference, sub='medidas'),
    steps('E-s9', 'errores', 'Dos instrumentos: error absoluto frente a relativo', gen.two_instruments, sub='escala'),
    steps('E-s10', 'errores', 'Truncamiento al cortar la serie de e', gen.series_truncation, sub='origen'),
    steps('E-s11', 'errores', 'Redondeo a k decimales y su cota', gen.rounding_bound, sub='representacion'),
    steps('E-s12', 'errores', 'De un error porcentual al error absoluto', gen.percent_to_absolute, sub='tolerancia'),
]

BANK = {q['id']: q for q in MULTI + OPEN + STEPS}


def outline():
    """El banco organizado por tema (y, en errores, por subtema): lo que ve el estudiante en la pantalla de inicio."""
    rows = []
    for topic, (title, url, _template) in SOURCES.items():
        questions = [q for q in BANK.values() if q['topic'] == topic]
        item = {'topic': topic, 'title': title, 'url': url, 'total': len(questions),
                'multi': sum(q['type'] == 'multi' for q in questions), 'open': sum(q['type'] == 'open' for q in questions),
                'steps': sum(q['type'] == 'steps' for q in questions), 'subtopics': []}
        if topic == 'errores':
            item['subtopics'] = [{'key': key, 'title': name, 'total': sum(q.get('sub') == key for q in questions)}
                                 for key, name in SUBTOPICS.items()]
        rows.append(item)
    return rows
assert len(BANK) == len(MULTI) + len(OPEN) + len(STEPS), 'identificadores de pregunta duplicados'


def instantiate_steps(question, seed):
    return question['generator'](random.Random(f'{question["id"]}:{seed}'))
