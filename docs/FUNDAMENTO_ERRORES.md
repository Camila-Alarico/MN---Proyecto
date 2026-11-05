# Fundamento académico de la práctica de errores

Revisión del 29/10/2026. Estas fuentes se eligieron para fundamentar esta mejora;
no se presentan como bibliografía exigida por la profesora ni como sustituto del
sílabo. La redacción y los ejercicios de NumLearn son propios.

## Referencia principal

Tobin A. Driscoll y Richard J. Braun, *Fundamentals of Numerical Computation*,
edición en línea, sección 1.1, [Floating-point numbers](https://fncbook.com/floating-point/).
El libro distingue precisión de exactitud y describe la distancia absoluta, su
medida relativa y las limitaciones de la representación finita.

Con una referencia conocida \(v\) y una aproximación \(\widetilde v\), la práctica
usa medidas no negativas:

\[
E_a=|v-\widetilde v|,\qquad
E_r=\frac{E_a}{|v|}\quad(v\ne0),\qquad
E_p=100E_r\;\%.
\]

El absoluto conserva las unidades; el relativo es una proporción. La aplicación
mantiene esa convención en etiquetas y correcciones. Si la referencia es cero,
el relativo no se define; la teoría, el explorador y la práctica permiten comprobar ese caso. No definido no significa cero.

## Origen y propagación de errores

La [Lecture 1.2: Errors of numerical approximations](https://dmpeli.math.mcmaster.ca/Matlab/CLLsoftware/NumMethods/Lecture1-2.html),
de McMaster University, distingue representación con cifras finitas y aproximación
de procesos mediante una cantidad finita de términos. Sirve para separar el
redondeo del truncamiento de un método; no se copiaron sus tablas numéricas.

La sección [Problems and conditioning](https://fncbook.com/conditioning/) de
Driscoll y Braun complementa el tema: perturbaciones pequeñas de entrada pueden
amplificarse según el problema. Por eso un resultado debe interpretarse respecto
a la escala de los datos, no solo por los decimales que muestra.

## Regla de tolerancia de esta actividad

NumLearn declara una tolerancia **absoluta** y usa la regla inclusiva
\(E_a\le\tau\). Por tanto, la igualdad se acepta. Es el criterio indicado en
el ejercicio; no debe aplicarse la misma comparación a un porcentaje sin cambiar
también el tipo de tolerancia.

La tolerancia del problema es distinta del margen usado por el corrector para
admitir una respuesta redondeada. Este último mantiene tolerancias absoluta
`5e-6` y relativa `1e-6`, con indicación de conservar seis decimales si se redondea.

## Comprobación del caso aportado por la usuaria

Este desarrollo es propio y fue verificado con el código:

\[
v=20,\quad\widetilde v=19.5,\quad\tau=0.5;
\qquad E_a=0.5,\quad E_r=0.025,\quad E_p=2.5\%.
\]

La elección correcta es «Sí, cumple», porque \(0.5\le0.5\). Escribir `0.5` como
relativo repite el absoluto; escribir `0.2` como porcentaje tampoco satisface
la conversión. El corrector identifica cada campo por separado, conserva los
aciertos y explica el caso de igualdad.

Un ejemplo resuelto con **otros datos** queda plegado en la actividad. Es una
decisión didáctica de esta implementación: permite consultar el procedimiento
sin sustituir de entrada los valores del ejercicio del estudiante.

## Representación matemática y comprobaciones

Se usa MathJax 3.2.2, servido localmente, para representar LaTeX como SVG. El
contenido dinámico se procesa de nuevo al cambiar de paso y se limpia antes de
retirarlo, siguiendo la API de [MathJax para contenido dinámico](https://docs.mathjax.org/en/v3.2/advanced/typeset.html).
Si el motor falla, permanece texto matemático legible.

Las pruebas cubren la igualdad con la tolerancia, referencias negativas,
confusiones entre relativo y porcentaje, corrección parcial, delimitadores TeX,
recarga de contenido y representación en Chrome con los CDN bloqueados.
La fundamentación matemática fue consultada en las fuentes enlazadas; la
propuesta visual y los mensajes específicos son decisiones propias del proyecto.


## Alcance de la entrega centrada en errores

El banco principal tiene 20 preguntas originales: orígenes y medidas del error,
unidades, referencia cero, escala, tolerancia, redondeo y truncamiento. Cada
intento toma cinco preguntas de conceptos y después cinco de aplicación, sin
preguntas de búsqueda de raíces ni de sistemas lineales.

Hay 12 ejercicios guiados de errores. Se conservan seis casos anteriores y se
completan con comparación de redondeo y truncamiento de una misma referencia,
un límite decimal, referencia cero y dos escalas con la misma proporción.
Las referencias decimales de constantes se tratan como datos escritos del
enunciado, no como representaciones exactas de números irracionales.

En referencia cero se pregunta explícitamente si Er y Ep están definidos; no
se solicita introducir un número en una división imposible. Se sigue evaluando
Ea y su tolerancia. La respuesta incorrecta explica la diferencia entre cero y
una medida no definida.

El explorador también compara la tolerancia en el servidor. Su resta y sus
límites usan Decimal sobre los datos decimales normalizados, evitando rechazar
la igualdad 1.1 − 1 = 0.1 por la representación binaria. El botón de límite exacto
usa esos mismos extremos. Esto no cambia la precisión de los algoritmos de raíces.
