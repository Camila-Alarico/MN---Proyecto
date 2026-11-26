# NumLearn — Retroalimentación de la profesora

**Fecha de la presentación:** 22 de octubre de 2026

**Curso:** Métodos Numéricos — UNSA

Este documento reúne las observaciones realizadas por la profesora durante la presentación de NumLearn, junto con los apuntes de un integrante del equipo.

La indicación principal para la siguiente clase fue **escoger el módulo que esté más avanzado y terminarlo bien**, en lugar de intentar desarrollar todos los módulos simultáneamente.

## 1. Transcripción del audio 1 — 11.mp4

*Duración: 8 minutos y 43 segundos. Transcripción con puntuación y pequeños ajustes de legibilidad. Algunos fragmentos tienen reconocimiento de voz impreciso.*

### Presentación de los módulos

**Estudiante:** Errores, con un módulo adicional donde dice errores, tipos de errores. Ya, si hablamos de ecuaciones no lineales, están los métodos cerrados acá y los métodos abiertos. Estamos en bisección, regla falsa, métodos abiertos, punto fijo, Newton-Raphson, secante y raíces múltiples.

**Profesora:** ¿Y han modificado?

**Estudiante:** Sí, lo modificamos un poco en cuanto al orden. La verdad está un poco más variado, con muchos más módulos y cosas. Pero en lo que más estuvimos trabajando fue el módulo dos de sistemas lineales, donde tenemos la parte de la teoría.

Eliminación gaussiana y Gauss-Seidel. Ahora, si queremos practicar, acá tenemos, en métodos directos, eliminación gaussiana. Tenemos la calculadora, que ahora sí probamos que resuelva correctamente.

Acá tenemos casos base. Por ejemplo, este es el caso que estaba en la teoría. Entonces lo resolvemos y nos muestra...

**Profesora:** Paso por paso.

**Estudiante:** Paso por paso lo que hace.

**Profesora:** Y la solución. Ya, resume. Has colocado los datos así.

**Estudiante:** Sí.

### Observación sobre el pivoteo

**Profesora:** Si yo pongo datos muy dispersos, con decimales, ¿sí? Y con decenas y centenas. ¿Recuerdan que les dije lo del pivoteo?

**Estudiante:** Sí.

**Profesora:** ¿Están teniendo en cuenta el pivoteo?

**Estudiante:** Si no me equivoco, sí. A ver... Muestra el de Seidel primero.

**Profesora:** Ese es el criterio de convergencia.

**Estudiante:** Sí, acá converge y no converge.

**Profesora:** Esos son de diagonal principal. Tiene que estar más claro.

**Estudiante:** Entonces, tendríamos que cambiar la matriz, ¿no?

**Profesora:** No, no, no. La matriz puede ser cualquiera. Cuando yo analizo los datos de la matriz, si yo tengo 0.01 como en el primer dato, X uno, pero por ahí tengo uno de 100, que es por ejemplo X tres tres, 100, yo ese 100 tengo que mover para el uno uno.

Porque recuerda el error de redondeo. La ecuación principal se queda estática. Entonces, los mejores datos, los más redonditos, y números más grandes. Por eso es pivoteo, elemento de pivote.

**Estudiante:** Creo que no lo pensamos, pero...

**Profesora:** En muy pocos sistemas que diseñan se ve el tema del pivoteo. Por eso, si pueden hacerlo, lo hacen. Si no lo pueden, lo dejan, pero tienen que indicar que el pivote pueden colocarlo de antemano.

Porque programar realmente es difícil. Entonces, el trabajo previo: determinar elemento pivote, acomodar la matriz, pueden colocarlo en su teoría y cuando están haciendo prácticas lo pueden hacer como preguntas o pasos a seguir.

Igual como revisan el criterio de convergencia, revisan si es una matriz diagonalmente dominante, igual pueden determinar cuál es el elemento pivote.

Entonces, antes de ingresar los datos a su matriz, ya lo ordena la persona y lo sube correcto.

**Estudiante:** Entonces ya la máquina no lo hace.

**Profesora:** Sí.

**Estudiante:** Ah, enseñar eso antes.

**Profesora:** Sí, pero tienes que enseñar, dar retroalimentación.

### Observaciones sobre la interfaz

**Profesora:** Ahí ustedes colocaron demasiados textos.

**Estudiante:** Mucho texto.

**Profesora:** Mucho texto. Y hasta, por ejemplo, «Mi progreso». ¿Qué cosa tienen ahí?

**Estudiante:** Era solo como una...

**Otro estudiante:** Como un sistema de usuario.

**Estudiante:** Que pueda marcar que completó un tema o no completó.

**Otro estudiante:** El usuario puede tener un progreso.

**Profesora:** Ya, el progreso lo botan al final.

Lo primero se va a teoría. Y les recomiendo que lo pongan ahí principal. Como un principal. Y ahí donde dice teoría, laboratorio, se dejan así.

Para cada método, no sé. Pero para que no sea tanto cansancio visual, porque está solamente en esta pantalla, lo dividen un poquito.

Acá ponen lo principal, por ejemplo los recursos, teoría, práctica, como quieran. Y en otro menú ahí ponen tema uno, tema dos, tema tres. Y en cada tema ya lo desglosan.

Lo pueden dejar así, pero que se cierre automáticamente.

**Estudiante:** Sí, no es tan visible.

### Observación sobre la búsqueda

**Profesora:** ¿Ustedes colocaron la búsqueda?

**Estudiante:** Sí.

**Profesora:** Puede ser colocar esa búsqueda. Por ejemplo, buscar el tema. No en la lista, sino escribir «Quiero Newton».

**Estudiante:** Ya, ya.

**Profesora:** Y te manda donde tú quieres. Ordénalo un poquito. Porque está bonito, idea bonita, pero falta pulir.

**Estudiante:** Orden y detalle.

### Observación sobre evaluaciones y autoevaluación

**Profesora:** ¿Tiene evaluación? ¿Tiene evaluación o algo?

**Estudiante:** Eh...

**Otro estudiante:** No sé si habrá documento de evaluación.

**Profesora:** Pero fíjense qué cosa pueden hacer.

Evaluación sí, porque si no mides si aprendieron. Con seis preguntas no vas a poder.

Tienen que hacer como un banco de preguntas. Primero pongan preguntas teóricas. Si dominan teoría, después las preguntas prácticas.

Pregunta práctica: ¿qué les interesa?

Yo pongo la respuesta, me dice que está bien o está mal. Si está bien, no me dice nada, solo me dice «OK». Pero si está mal...

**Estudiante:** Le explica por qué.

**Profesora:** Dónde estoy mal. ¿Entienden?

Por eso, cuando está en autoevaluación, cuando yo estoy resolviendo, me pones el enunciado.

Entonces, primero, ¿qué tengo que determinar?

¿Qué tipo de problema es? ¿De qué estoy hablando? ¿Qué método utilizo?

Eso tengo que escoger primero.

**Estudiante:** Ah, ya, sí.

**Profesora:** Ya escogí esto. Si está check, entonces recién puedo calcular.

Porque si escogí mal, ¿qué voy a calcular?

Y que me salgan algunos datos aleatorios, no sé si les parece interesante.

Pero como les digo, no es necesario que implementen todo. Hagan dos, tres, pero bien.

**Estudiante:** Bien, ya.

**Profesora:** Porque si ustedes hacen dos, tres bien, los demás la IA los va a ayudar.

La IA sí está bien, pero ¿cómo lo usan? En documentación tienen que poner qué han usado, qué IA han usado, cuál es su trabajo, cuál es el trabajo...

*El audio termina durante la explicación sobre documentación e inteligencia artificial.*

---

## 2. Transcripción del audio 2 — 22.mp4

*Duración: 2 minutos y 56 segundos. Intervención principalmente de la profesora.*

### Observaciones sobre el diseño

**Profesora:** Ahora, ese es uno.

Segundo, cuando ustedes están diseñando páginas web, ¿les gusta tener demasiada...?

¿Me gusta pasar un scroll de Twitter como de cinco minutos hasta abajo?

Si no te gusta, ¿para qué lo haces?

### Observaciones sobre cómo se resuelven ejercicios

Ahora, yo les pregunto: si me están dando un ejercicio para resolver, yo lo tengo que resolver, ¿sí?

¿Cómo ustedes resuelven ejercicios, supuestamente?

No cuando resuelve IA, sino cuando ustedes están resolviendo.

¿Qué cosa tienen que hacer?

¿No tienen que escoger los datos iniciales?

No siempre te dan los datos iniciales, ni intervalo ni nada.

¿De dónde sacas esos datos iniciales? ¿Del dedo? No.

Tienes que graficar la función para que me dé el intervalo.

No he visto ninguno que haya hecho eso.

Entonces primero es separar las raíces, ¿recuerdan? F de xi. El siguiente.

OK, yo separé raíces.

¿Qué método utilizo?

¿Cualquiera?

Yo me pongo en que la máquina me diga: «¿Y por qué vamos a hacer eso?».

¿Te puede recomendar o no te puede recomendar?

Ahora ya escogí método, todo. Puse los datos iniciales, todo.

Ahora sí puedo presionar el botón mágico: resolver.

Pero ¿resolver qué?

¿Que la máquina me resuelva o yo tengo que retroalimentar, por lo menos colocar cuál es el X y cuál es el error de ese X?

Y ahora, si yo he hecho bien el trabajo, la máquina me tiene que decir: «Aplauso, has hecho bien».

Y si me fui por el camino del error, ya carita triste, carita enojada, lo que quieran.

Pero me tienen que explicar dónde me equivoqué y mostrar el mejor camino.

Ahora recuerden que ustedes son muy sabios, ¿ah? La primera vez se han equivocado...

*Fin del segundo audio.*

---

## 3. Apuntes de Andrés — 22 de octubre de 2026

Estos son los apuntes adicionales tomados durante la presentación.

### Mensaje de las 3:05 p. m.

- Errores y tipos de errores.
- Considerar el pivoteo con decimales, ejemplo de 0.01 a 100.
- Determinar el elemento pivote.
- Incorporar pasos a seguir en las prácticas.
- Reducir el texto.
- Colocar «Mi progreso» al final.
- Quitar «Mis apuntes» y dejar principalmente la teoría.
- Añadir dos menús: uno lateral con las secciones principales y otro horizontal.
- Colocar la búsqueda arriba, con una lupa, para buscar temas.
- Implementar evaluación para el estudiante.
- Primero preguntas teóricas y después prácticas.
- Si una respuesta práctica es correcta, basta una confirmación sencilla.
- Si es incorrecta, mostrar dónde está el error.
- Incorporar un proceso guiado en el que el estudiante identifique el tema y elija el método antes de resolver el ejercicio.

### Mensaje de las 3:07 p. m.

Andrés aclaró que:

- La profesora dijo que los errores y tipos de errores deben estar en una sección aparte.
- Se debe considerar el pivoteo con decimales.
- La profesora utilizó como ejemplo los coeficientes X11 = 0.01 y X33 = 100.
- Se debe considerar el elemento pivote o enseñar indirectamente al usuario cómo utilizar el pivoteo.

### Mensaje de las 3:17 p. m.

**«Próxima clase terminar 1 módulo, escoger el que más...»**

La anotación termina incompleta, pero indica que deben escoger un módulo, aparentemente el más avanzado, y terminarlo para la siguiente clase.

---

## 4. Resumen consolidado de lo que quiere la profesora

### A. Prioridad principal

**Terminar bien un solo módulo para la siguiente clase.**

La profesora enfatizó que no es necesario implementar todo. Indicó que es preferible desarrollar dos o tres experiencias o funcionalidades bien hechas, en lugar de muchas incompletas.

No especificó en los audios cuál de los módulos debe seleccionarse.

### B. Contenido matemático

**Errores:**

- Separar errores y tipos de errores en una sección.
- Enseñar cómo interpretar errores numéricos.

**Pivoteo:**

- Considerar coeficientes con magnitudes muy diferentes.
- Determinar correctamente el elemento pivote.
- Enseñar al usuario a preparar los datos cuando no sea posible automatizar todo el procedimiento.

**Ecuaciones no lineales:**

- Graficar la función antes de resolver cuando corresponda.
- Separar o identificar las raíces.
- Determinar intervalos o valores iniciales adecuados.
- Identificar qué método conviene utilizar.

### C. Enseñanza y práctica

La profesora quiere que NumLearn no se limite a entregar automáticamente el resultado.

El estudiante debería participar en el proceso:

- Identificar el tipo de problema.
- Seleccionar el método correspondiente.
- Preparar los datos necesarios.
- Realizar cálculos o iteraciones.
- Comprobar respuestas.
- Comprender por qué una respuesta es incorrecta.

La plataforma debería ayudar al estudiante a aprender el procedimiento, no únicamente mostrar una respuesta final.

### D. Evaluación

- Incorporar evaluaciones de aprendizaje.
- Tener más de seis preguntas disponibles, mediante un banco de preguntas.
- Evaluar primero conocimientos teóricos.
- Después evaluar la resolución práctica.
- Permitir identificar el método antes de realizar los cálculos.
- Proporcionar retroalimentación específica cuando existan errores.
- Considerar valores o ejercicios variables.

### E. Interfaz y navegación

- Reducir el exceso de texto.
- Evitar páginas demasiado largas y con mucho desplazamiento vertical.
- Separar mejor los contenidos.
- Simplificar el menú lateral.
- Incorporar una segunda navegación para los temas.
- Colocar el progreso en una ubicación secundaria.
- Reducir o quitar la sección de apuntes de la navegación principal.
- Priorizar teoría y práctica.
- Incorporar una búsqueda visible que permita escribir el nombre de un tema, como Newton, y acceder directamente a él.

### F. Documentación

- Especificar qué herramientas de inteligencia artificial se utilizaron.
- Explicar qué tareas fueron realizadas por el equipo y cuáles recibieron apoyo de IA.

---

## 5. Aclaraciones importantes

**Sobre los libros:** En los dos audios no se mencionan libros, autores ni ejercicios bibliográficos específicos. La bibliografía aparece en el sílabo, pero no forma parte de las indicaciones verbales recogidas en estas grabaciones.

**Sobre el módulo a terminar:** La profesora no indicó explícitamente que deban escoger ecuaciones no lineales o sistemas lineales. Según los apuntes de Andrés, deben seleccionar el módulo más avanzado y completarlo para la próxima clase.

**Sobre el pivoteo:** La profesora dio el ejemplo de 0.01 y 100 para explicar la importancia del elemento pivote y los errores de redondeo. La explicación fue oral y no constituye por sí sola un algoritmo completo de pivoteo.

**Sobre las evaluaciones:** La profesora no exigió que todas las funcionalidades propuestas estén implementadas inmediatamente. Señaló que es preferible realizar pocas actividades bien desarrolladas.

**Sobre las mejoras:** Este documento registra la retroalimentación de la presentación. No contiene decisiones de implementación ni un plan de desarrollo.

## 6. Idea central de la retroalimentación

NumLearn debe ser una herramienta que permita al estudiante **aprender a resolver problemas de métodos numéricos**, no solamente introducir datos y recibir resultados.

La profesora dio especial importancia a comprender el problema, elegir un método adecuado, preparar los datos, trabajar con aproximaciones y errores, y recibir retroalimentación cuando el estudiante se equivoca.

Para la siguiente presentación, la prioridad registrada es **mostrar un módulo bien terminado**, con una experiencia educativa clara, matemática correcta y una interfaz mejor organizada.
