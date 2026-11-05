# Fundamento de las actividades del módulo 1

Referencia de la ampliación general anterior (`f64bc6a`). La entrega actual se centra en Errores; véase [Fundamento de errores](FUNDAMENTO_ERRORES.md).

Revisión: 29/10/2026. Son referencias consultadas para esta mejora, no libros
asignados por la profesora. Los enunciados, preguntas y mensajes de NumLearn son
originales; no se copiaron bancos de ejercicios de las fuentes.

| Contenido | Referencia consultada | Aplicación en NumLearn |
| --- | --- | --- |
| Errores absolutos y relativos | Driscoll y Braun, *Fundamentals of Numerical Computation*, [1.1](https://fncbook.com/floating-point/) | Distinguir distancia, proporción y escala. Véase [fundamento detallado](FUNDAMENTO_ERRORES.md). |
| Bisección | Autar Kaw, *Numerical Methods with Applications*, [3.03](https://nm.mathforcollege.com/NumericalMethodsTextbookUnabridged/chapter-03.03-bisection-method-for-solving-a-nonlinear-equation.html) | Continuidad, signos opuestos y punto medio. |
| Regla falsa | MIT, *10.001: Solution of Non-Linear Algebraic Equations*, [False Position](https://web.mit.edu/10.001/Web/Course_Notes/NLAE/node5.html) | Recta entre extremos y conservación del cambio de signo. |
| Newton | Driscoll y Braun, [4.3](https://fncbook.com/newton/) | Tangente, primera derivada y dependencia del inicio. |
| Secante | Driscoll y Braun, [4.4](https://fncbook.com/secant/) | Aproximar la pendiente con dos puntos. |
| Punto fijo | Driscoll y Braun, [4.2](https://fncbook.com/fixed-point/); Kværnø, Grasmair y Pacheco, [notas NTNU](https://www.math.ntnu.no/emner/TMA4130/2022h/html_notes/NonLinearEquations_v2.html) | Equivalencia, diagonal y=x e intervalos de contracción preparados. |
| Multiplicidad | Driscoll y Braun, [4.3](https://fncbook.com/newton/) | Newton ordinario pierde la convergencia cuadrática habitual en raíces múltiples. |

La variante de raíces múltiples conserva la fórmula ya presente en el proyecto.
Puede derivarse aplicando Newton a h=f/f′, donde se pueda calcular:

\[
h'=\frac{(f')^2-ff''}{(f')^2},\qquad
x_{n+1}=x_n-\frac{ff'}{(f')^2-ff''}.
\]

Esta derivación explica qué variante se practica; no atribuye esa fórmula
específica a un pasaje del libro que solo discute la multiplicidad.

## Diseño de las preguntas

Las preguntas comprueban decisiones y errores frecuentes: confundir error y
residuo, aplicar la cota de bisección a regla falsa, suponer que dos puntos
siempre forman un encierro, dividir por una derivada nula, confundir g(x)=0
con g(x)=x y perder raíces de multiplicidad par al buscar solo cambios de signo.

Los 36 ejercicios no equivalen a 36 problemas de contexto diferentes: hay
variantes de datos y funciones para practicar el mismo procedimiento. Cada
actividad exige identificar el problema y el método, preparar datos a partir
de una gráfica cuando corresponde, calcular y comprobar. La cantidad se combina
con un recorrido corto por pantalla; no se presenta todo el banco a la vez.

## Datos y condiciones verificadas

- Errores: seis referencias no nulas de distintas escalas y signos; incluye
  igualdad con la tolerancia y aproximación por exceso.
- Bisección, regla falsa, Newton y secante: tres cuadráticas, una cúbica,
  una función con coseno y otra con exponencial, continuas en el rango mostrado.
- Punto fijo: cos(x) y exp(−x) en [0.25,1], y (x+2/x)/2 en [1,2]. Cada
  transformación lleva su intervalo a sí mismo y tiene |g′| acotada por q<1.
- Raíces múltiples: (x−r)²(x+r+1), con r=1,2,3. La raíz positiva es doble;
  su signo no cambia al atravesarla. Los inicios se comprueban con el servicio.

El corrector de raíces usa el mismo motor que la calculadora. Las pruebas de
las actividades calculan independientemente el primer paso y sus medidas para
los 36 casos. La regla falsa verifica los extremos nuevos; los métodos abiertos
separan tamaño del paso y residuo. Completar una iteración no demuestra por sí
solo la convergencia del recorrido completo ni el dominio de todo el tema.
