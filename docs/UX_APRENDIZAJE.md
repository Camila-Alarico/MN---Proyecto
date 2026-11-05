# Recorrido de aprendizaje: Errores numéricos

Actualización del 29/10/2026 sobre `f64bc6a`. El equipo confirmó que esta entrega
se centra en **un tema, Errores numéricos**, en vez de ampliar todo el módulo.
Se conserva la [retroalimentación original](../RETROALIMENTACION_PROFESORA.md)
sin modificarla para atribuirle esa decisión posterior del equipo.

## Recorrido principal

Portada → Teoría de errores → Práctica de errores → Autoevaluación de errores.
El menú identifica el tema. Ingresar, progreso, favoritos y apuntes siguen fuera
de la interfaz. Los demás temas se conservan en un acceso secundario y en
`/ecuaciones-no-lineales/teoria/?vista=modulo`. Sus calculadoras mantienen todos
los controles y el comportamiento de la revisión anterior.

`/ecuaciones-no-lineales/teoria/` redirige a la URL canónica de errores. La página
separa tres paneles con navegación por teclado:

1. **Conceptos y medidas:** referencia, aproximación, Ea, Er, Ep y tolerancia.
2. **Origen del error:** redondeo, truncamiento y propagación. El ejercicio del
   informe sobre amplificación queda como profundización plegada.
3. **Explorador:** calculadora de errores, recta, tolerancia, ejemplos, control de
   aproximación, límite exacto, decimales mostrados y sustitución de las fórmulas.

Las fórmulas usan MathJax local con alternativa legible. El explorador conserva
sus controles y corrige la comparación de igualdades decimales: el servidor
calcula la distancia y los límites de tolerancia con Decimal; la interfaz usa
esa respuesta para el veredicto y el botón de límite.

## Práctica

`/ecuaciones-no-lineales/practica/` muestra **12 ejercicios de errores**. Los
filtros refuerzan habilidades del mismo tema, sin mezclar métodos:

| Grupo | Actividades |
| --- | --- |
| Medidas y datos | Referencia, aproximación y diferencias por defecto o exceso. |
| Escalas | Magnitudes grandes y pequeñas; misma proporción a otra escala. |
| Representación | Redondear y truncar una misma referencia. |
| Límites | Igualdad con la tolerancia y referencia cero. |

Se muestran seis tarjetas por vez, con nivel y objetivo. Cada ejercicio sigue
Comprender → Elegir la medida → Preparar → Calcular → Comprobar. Un fallo mantiene
el paso; la corrección es específica y conserva los aciertos. Una respuesta
correcta recibe confirmación breve. La actividad acaba enlazando la evaluación
del tema; también se puede repetir con otro caso.

Si v=0, Er y Ep se responden mediante opciones conceptuales: no se fuerza una
entrada numérica. El resultado distingue «no definido» de cero y conserva la
comparación absoluta con la tolerancia. Para v≠0 se comprueban las tres medidas.

Las respuestas aceptadas se normalizan al resultado interno; el corrector admite
redondeo con tolerancia absoluta 5e-6 y relativa 1e-6. Ese margen no es la tolerancia
del problema. Las referencias decimales dadas son los datos del enunciado.

## Autoevaluación

`/ecuaciones-no-lineales/autoevaluacion/` usa **20 preguntas originales de errores**.
Cada intento elige cinco de conceptos y después cinco de aplicación, todas
distintas. La interfaz señala la fase. Cuenta la primera respuesta, explica los
fallos y muestra qué repasar. La meta es **8 de 10**; no se presenta como una
certificación de dominio del tema.

La solución no se envía antes de responder. El servidor valida el intento y su
posición. Los intentos centrados en errores se guardan en claves de sesión
separadas, para que una recarga no recupere una actividad mezclada de la revisión
anterior. No hay nuevas tablas, migraciones ni registro permanente de notas.

## Contenido complementario

El catálogo general conserva 42 ejercicios en total, incluidos los 12 de errores,
y el banco general conserva 48 preguntas para compatibilidad. La evaluación
principal no utiliza ese banco mezclado. Los enlaces explícitos de métodos
abren su práctica complementaria; no redirigen sus cálculos hacia errores.
Los algoritmos de raíces, Gauss y Gauss-Seidel se conservan.

Las cuentas y sus datos anteriores tampoco se borran. Los módulos 3–5 continúan
pendientes. Completar este recorrido no equivale a terminar todo el módulo 1.

## Fuentes y uso de IA

El [fundamento de errores](FUNDAMENTO_ERRORES.md) identifica las referencias:
Driscoll y Braun, *Fundamentals of Numerical Computation*, y las lecciones de
McMaster sobre errores. Las preguntas y ejercicios son originales; no se
atribuyen a la profesora libros que no mencionó en las transcripciones.

Codex apoyó la investigación, la redacción de actividades, la reorganización y
las pruebas. El equipo eligió el tema y el alcance. Las respuestas se comprueban
con código determinista; no se envían a una IA. El equipo debe completar el
registro de otras herramientas usadas en etapas anteriores.

## Comprobación

```sh
.venv/bin/python manage.py test
npm test
NUMLEARN_TEST_SERVER=1 npm run test:browser
```

Las pruebas verifican el aislamiento entre sesiones, las 20 preguntas del tema,
el orden conceptos/aplicación, referencia cero, igualdad decimal, retroalimentación,
recarga y los 42 ejercicios conservados. Chrome cubre el recorrido principal,
accesibilidad, móvil y todas las funciones de los seis simuladores de raíces.
Se prueba también la actividad con CDN bloqueados. Una revisión visual adicional
comprueba la gráfica con Plotly. La accesibilidad automática no sustituye la
observación con estudiantes y lectores de pantalla.
