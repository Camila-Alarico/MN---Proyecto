# Evaluación y autoevaluación (app `assessment`)

Objetivo: que el estudiante demuestre comprensión del procedimiento y no solo obtenga una respuesta.

## Qué incluye
| Pieza | Dónde |
|---|---|
| Banco de preguntas de selección múltiple, abiertas y paso a paso | `assessment/bank.py` |
| Generadores de problemas con datos distintos por intento | `assessment/generators.py` |
| Composición aleatoria, corrección y reinicio de intentos | `assessment/engine.py`, `assessment/views.py` |
| Interfaz de autoevaluación | `templates/assessment/page.html`, `static/js/assessment/assessment.js` |

Cada pregunta se vincula con el tema real correspondiente (`SOURCES` en `bank.py`).

## Formatos y evaluación
* **Selección múltiple:** opciones mezcladas en cada intento y crédito parcial.
* **Respuesta abierta:** rúbrica de conceptos, mínimo de palabras y explicación en lenguaje propio.
* **Problema paso a paso:** datos variables, pasos bloqueados y corrección en el servidor.
* **Orden:** se seleccionan las cantidades previstas de cada formato y luego se mezcla la secuencia completa; por tanto, los tipos aparecen intercalados y el orden puede cambiar en cada intento.

## Alcances
`errores`, `modulo-1`, `modulo-2` y `curso`. La ruta `/ecuaciones-no-lineales/autoevaluacion/` abre el alcance de errores numéricos.

La interfaz no revela el tamaño del banco ni cuántas preguntas contiene cada evaluación.

## Regla de salida de la práctica
Antes de empezar se informa que, si el estudiante sale de la práctica o cambia de pestaña y permanece fuera más de 5 segundos, el intento se reinicia completamente. La sesión conserva únicamente una marca temporal privada para aplicar esta regla. No se registran eventos de salida, duración, copias ni pegados, y esa información no se muestra a docentes.

## Cómo verificar
1. Ejecutar `python manage.py test assessment.tests`.
2. Iniciar una evaluación y comprobar que aparecen formatos distintos intercalados.
3. Repetir el intento y comprobar que el orden cambia.
4. Cambiar de pestaña y regresar antes de 5 segundos: el intento debe conservar el progreso.
5. Cambiar de pestaña y regresar después de más de 5 segundos: debe comenzar un intento nuevo desde la primera pregunta.
6. Recargar o salir de la página durante más de 5 segundos y volver: también debe comenzar un intento nuevo.
7. Revisar la pantalla inicial y confirmar que no se muestra el tamaño del banco ni el total de preguntas.
