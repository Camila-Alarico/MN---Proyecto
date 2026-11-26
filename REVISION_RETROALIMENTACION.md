# NumLearn — revisión de la retroalimentación y prioridades

Revisión del **29/10/2026**, sobre el commit **`6fe5280`**.

**Diagnóstico previo a los cambios de UX.** Después se implementaron localmente
la nueva navegación, tres prácticas guiadas y una autoevaluación con banco de
preguntas. El estado de esa implementación y sus límites están en
[UX de aprendizaje](docs/UX_APRENDIZAJE.md). La tabla siguiente conserva el
contraste original para entender el motivo de los cambios.

Fuente: [documento proporcionado por el equipo](RETROALIMENTACION_PROFESORA.md).
Se contrastó su contenido con el código actual. Esta revisión no volvió a
transcribir ni verificó los videos originales. Las propuestas siguientes son
recomendaciones de trabajo, distintas de lo que la profesora dijo literalmente.

## Qué cambia en el objetivo

La siguiente entrega debe demostrar aprendizaje en **un módulo elegido**.
La calculadora, las tablas y los ejemplos resueltos son una base. Falta una
experiencia en la que el estudiante tome decisiones, realice cálculos y reciba
retroalimentación sobre sus propias respuestas.

La profesora no escogió explícitamente un módulo, no pidió desarrollar los cinco
para la próxima clase y no fijó una cantidad exacta de preguntas para el banco.
Los datos aleatorios son una posibilidad mencionada, no una obligación de
generar inmediatamente todos los ejercicios de forma automática.

## Qué ya existe y qué falta

| Observación | Estado actual | Diferencia pendiente |
| --- | --- | --- |
| Terminar un módulo | Hay dos módulos con calculadoras. | Elegir uno como prioridad y definir qué experiencia educativa se terminará. |
| Separar errores y tipos de errores | Existe `/ecuaciones-no-lineales/errores/`, con cálculo de error absoluto, relativo y porcentual. | Ampliar la enseñanza de redondeo, truncamiento y propagación; las menciones actuales no equivalen a una práctica guiada de esos tipos. La sección sigue perteneciendo al módulo 1, no es un módulo independiente. |
| Graficar antes de elegir datos iniciales | La búsqueda gráfica detecta muestras con cero e intervalos candidatos, y enlaza con bisección. | Integrarla en el recorrido del ejercicio; hoy aparece como herramienta opcional. |
| Elegir y justificar un método | Hay familias, selector, fórmulas y consejos. | Comprobar que el alumno identifica el tipo de problema y justifica una elección válida antes de calcular. |
| Calcular y comprobar una aproximación y su error | El servidor produce resultados, pasos y residuos; la lección de errores tiene interacción. | Pedir una respuesta al estudiante y detectar dónde se equivocó. Recorrer una tabla calculada no comprueba que sepa construirla. |
| Teoría antes de práctica evaluada | Hay teoría y ejercicios resueltos por método. | Crear evaluación de conocimientos previos y su transición a la práctica. |
| Banco de preguntas | El modelo antiguo de ejercicios e intentos se eliminó. | Construir un banco adecuado a la experiencia elegida, con más de seis preguntas disponibles y cobertura de objetivos. No basta con recuperar una pantalla antigua de quiz. |
| Retroalimentación de errores | Hay validaciones de entrada y avisos de fallos del algoritmo. | Añadir retroalimentación didáctica sobre respuestas del alumno: signo, intervalo, fórmula, sustitución, paso o residuo. |
| Pivoteo | Gauss ya hace pivoteo parcial automático y muestra intercambios. | Explicar el criterio y dar una actividad previa con magnitudes diferentes; distinguirlo de dominancia diagonal y pivoteo total. |
| Reducir texto y desplazamiento | Andrés agrupó el recorrido en seis y cuatro pasos. | Separar las actividades: las pestañas de los métodos son en gran parte enlaces a secciones de una misma página larga. |
| Priorizar teoría y práctica | Existen un menú lateral y navegación horizontal por método. | Ajustar su jerarquía: el simulador de raíces sigue siendo el primer bloque principal de su página. |
| Progreso secundario y apuntes fuera del menú principal | Hay un menú de perfil que también ofrece estos accesos. | El lateral todavía muestra progreso arriba y enlaces a «Mi progreso» y «Mis apuntes» antes de los temas. Se pueden reubicar sin eliminar los datos. |
| Búsqueda visible | Ya hay lupa y buscador superior; busca en ambos módulos sin distinguir tildes ni mayúsculas. | Buscar `Newton` funciona. Interpretar literalmente `Quiero Newton` y enviar directamente al método no está implementado. |
| Documentar la IA utilizada | La conversación permite identificar intervenciones de Codex. | Registrar con el equipo qué otras herramientas usaron, en qué tareas y qué verificaron personalmente. No inferir autoría por el nombre de un commit. |

Evidencia principal: [búsqueda](core/search.py), [menú lateral](templates/components/sidebar.html),
[barra superior](templates/components/navbar.html), [simulador de raíces](templates/nonlinear/simulator.html),
[pestañas](templates/components/method_tabs.html), [ejercicios resueltos](templates/components/worked_example.html),
[lección de errores](templates/nonlinear/errores.html), [búsqueda gráfica](static/js/nonlinear/graph-search.js)
y [Gauss](linear/services/direct.py).

## Precisión importante sobre el pivoteo

El programa actual **sí tiene pivoteo parcial**. En cada columna elige el
coeficiente de mayor valor absoluto entre las filas disponibles. Cambia filas
completas de la matriz aumentada, incluido `b`, para conservar las ecuaciones.
No elige el mayor número de toda la matriz ni intercambia columnas.

El ejemplo oral de llevar un `100` desde la posición `(3,3)` a `(1,1)` no describe
por sí solo ese algoritmo. Para desplazar un elemento de otra columna a la
primera también haría falta intercambiar columnas y mantener el orden de las
incógnitas. Esa es una operación distinta y debe explicarse con cuidado si se incorpora.

Comprobación realizada sobre el código actual:

```text
A = [ 0.01   1    1 ]       b = (5.01, 14, 304)
    [ 1      5    1 ]
    [ 2      1  100 ]

En la primera columna, el mayor valor absoluto es 2.
Gauss elige ese pivote e intercambia F1 y F3.
El 100 queda en la tercera columna; la solución sigue siendo (1, 2, 3).
```

El pivote se elige por magnitud según el criterio declarado, no por tener menos
decimales. La dominancia diagonal se usa para analizar convergencia de
Gauss-Seidel: no es lo mismo que seleccionar pivotes en Gauss.
Tampoco se debe presentar el aviso de pivote casi nulo como una demostración
exacta de singularidad: el programa aplica un umbral numérico.

## Módulo que convendría priorizar

**Mi recomendación es el módulo 1, ecuaciones no lineales y errores**, porque ya
reúne la mayor parte del recorrido que falta conectar: lección de errores,
búsqueda gráfica, métodos cerrados y abiertos, ejemplos y comparador.
No es una elección hecha por la profesora ni una decisión ya tomada por el equipo.

El esfuerzo principal sería integrar y evaluar ese recorrido. Para una entrega
acotada, propongo tres experiencias que reutilicen lo existente:

| Experiencia propuesta | Trabajo del estudiante | Resultado que habría que comprobar |
| --- | --- | --- |
| Errores y tolerancia | Distinguir las medidas de error, calcularlas e interpretar si una aproximación cumple. | Valores, unidades e interpretación; explicar, por ejemplo, la referencia cero o la confusión entre error y tolerancia. |
| Bisección desde la gráfica | Examinar la función, proponer un intervalo, justificar el método y escribir una iteración. | Signos de los extremos, punto medio, subintervalo, cota y residuo. |
| Newton con decisiones justificadas | Elegir un inicio, reconocer las condiciones del método y calcular una iteración. | Derivada, fórmula, nueva aproximación y distinción entre paso, error y residuo; explicar un fallo de derivada nula. |

El módulo 2 también es una opción válida si el equipo decide concentrarse en
Gauss y Gauss-Seidel. En ese caso, el recorrido guiado debe centrarse en formular
el sistema, identificar el pivote o la condición de convergencia y comprobar un
paso. Desarrollar ambas evaluaciones a la vez ampliaría el alcance de esta entrega.

Los módulos 3, 4 y 5 pueden continuar anunciados como pendientes.

## Qué significaría terminar la experiencia elegida

Un criterio de entrega propuesto, para discutir con el equipo:

1. Se ve una ruta corta con teoría, preparación, práctica y evaluación.
2. Hay un banco de preguntas teóricas con cobertura suficiente; una sesión puede
   usar una selección del banco, sin mostrar todas las preguntas en una pantalla.
3. En práctica se presenta primero el problema. El estudiante identifica su
   tipo y el método, y recibe una explicación si su elección no es válida.
4. El estudiante prepara datos iniciales y realiza al menos un cálculo antes de
   descubrir la solución completa. Si varios métodos sirven, no se penaliza una
   alternativa matemáticamente válida solo por no ser la esperada.
5. Las respuestas numéricas se comprueban con un criterio de tolerancia declarado,
   compatible con el redondeo pedido. No se comparan únicamente cadenas de texto.
6. Una respuesta correcta recibe confirmación breve. Una incorrecta señala el
   paso concreto y ofrece una pista para corregirlo, conservando el intento.
7. Se prueban rutas correctas e incorrectas, edición de datos, redondeo, entradas
   incompletas y funcionamiento en una pantalla pequeña.

Esto puede implementarse con reglas y cálculos verificables; no exige introducir
un tutor generativo para validar respuestas. Los datos variables pueden partir
de casos preparados con solución comprobada, manteniendo condiciones del método.

## Orden de trabajo propuesto

Primero elegir módulo, objetivos y experiencias. Después organizar las pantallas
alrededor de teoría, preparación y práctica; el progreso y los apuntes pasan a
un lugar secundario. A continuación conectar el banco teórico con los pasos
prácticos y sus mensajes de corrección. Finalmente validar matemáticas, interacción
y documentación de la entrega.

Los cambios de Andrés —familias, selector y ejemplos— sirven como base. La
siguiente tarea sería completar el trabajo del estudiante entre esos recursos.

Para documentar la IA, se pueden registrar desde ahora las tareas comprobadas de
esta conversación: revisión del ZIP y del código, configuración local, corrección
de respuestas desactualizadas, ejecución de verificaciones, operaciones de GitHub
y preparación de los Markdown con apoyo de Codex. El equipo debe completar las
herramientas usadas previamente y quién revisó cada resultado; esos datos no están
confirmados aquí.

Esta revisión solo añade documentación. No crea evaluaciones, modifica algoritmos
ni cambia la navegación de la página. La versión de referencia sigue siendo `6fe5280`.
