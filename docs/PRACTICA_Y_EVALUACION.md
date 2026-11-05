# Práctica con bloqueo, enunciados contextualizados y evaluación por módulo

Complementa `docs/EVALUACION.md`. Resume lo que cambió en la práctica de ecuaciones no lineales
(`/ecuaciones-no-lineales/practica/`) y en la evaluación.

## 1. Práctica individual: bloqueo al salir de la página
* **Detección (frontend, `static/js/nonlinear/activity.js`):** `visibilitychange` (pestaña oculta), `blur` de la ventana
  (con 0.4 s de margen para ignorar falsos positivos) y `pagehide` (cerrar, recargar o navegar). Al detectar la salida se
  envía `action: 'leave'` con `fetch(..., {keepalive: true})`.
* **Estado (backend, `nonlinear/learning.py` y `learning_views.py`):** `lock_practice()` marca `locked = True` en la
  sesión y cuenta el bloqueo. `public_practice()` devuelve solo el mensaje de bloqueo (sin datos ni pasos) y
  `check_practice()` rechaza cualquier respuesta. Recargar o volver más tarde muestra el bloqueo.
* **Repetir:** `action: 'restart'` crea un estado nuevo del **mismo ejercicio desde el paso 1** (id nuevo, errores en 0).
  El contador de bloqueos se conserva. Un aviso rezagado de una práctica anterior se ignora (por `id`).
* Una práctica terminada no se bloquea. Las fuentes (enlace externo) se abren al final: abrirlas durante la práctica la bloquearía.
* Límite: el bloqueo depende de que el navegador envíe el aviso. Quien desactive JavaScript o corte la red
  puede no ser detectado; la sesión no es una medida de seguridad fuerte sino una garantía de proceso.

## 2. Enunciados contextualizados
Los 54 ejercicios del banco de práctica traen un enunciado con situación, unidades y tolerancia
(`nonlinear/practice_bank.py`, campo `context`). Se agregaron ejercicios de mayor dificultad
(dosis pediátrica, tiempo de carga con límite, índice de crecimiento bacteriano, deflexión de una viga,
cadena de radicales). El enunciado se muestra antes de los datos y también en las tarjetas del banco.
Una prueba comprueba que cada ejercicio sigue siendo resoluble de principio a fin con cálculos independientes.

## 3. Banco de evaluación por tema
* Organizado por tema y, en errores, por subtema: Medidas del error, Origen y propagación, Tolerancia y decisión,
  Escala y referencia cero, Cifras y presentación (`assessment/bank.py`, `outline()`; visible en la pantalla de inicio).
* **Errores numéricos tiene 50 preguntas** (23 selección múltiple, 15 abiertas, 12 paso a paso). Los demás temas
  conservan su banco anterior (43 preguntas); el banco total es de 93.
* La búsqueda global (`core/search.py`, `/buscar/`) no se tocó.

## 4. Mezcla y variación
* Las opciones de selección múltiple se barajan al crear cada intento (`engine.compose`); en la práctica, las opciones
  de los pasos de elección se barajan una vez por intento (estable al recargar, distinta al repetir).
* Cada intento nuevo evita las preguntas de los dos últimos intentos del mismo estudiante mientras queden preguntas
  nuevas, se reparte entre subtemas y los problemas paso a paso generan datos nuevos con una semilla por intento.

## 5. Evaluación por módulo y revisión de errores
* Alcances: `errores`, `modulo-1`, `modulo-2`, `curso`. El estudiante elige uno al empezar.
* Al terminar, «Ver solo las preguntas que fallé» (`action: 'review'`) muestra únicamente las respondidas mal o a medias,
  con la respuesta del estudiante, la correcta y la explicación. Si el docente corrige una respuesta abierta a «correcta»,
  deja de aparecer. Una evaluación perfecta no tiene nada que revisar.

## Cómo verificar
`python manage.py test` (173 pruebas). Con navegador: practicar un ejercicio, cambiar de pestaña y volver (aparece el
bloqueo), recargar (sigue bloqueada), «Repetir desde el inicio»; terminar una evaluación y abrir la revisión.
