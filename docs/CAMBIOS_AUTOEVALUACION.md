# Correcciones de autoevaluación

Cambios aplicados a la autoevaluación del curso y a `/ecuaciones-no-lineales/autoevaluacion/`:

1. La pantalla inicial conserva un selector visible para elegir entre el módulo 1, el módulo 2, el curso completo y la evaluación específica del tema de errores.
2. La ruta de autoevaluación del módulo 1 selecciona por defecto el módulo 1 completo; ya no entra directamente a la evaluación exclusiva de errores numéricos.
3. Cada opción describe el contenido que se evaluará, sin mostrar el tamaño del banco ni el número total de preguntas.
4. Los formatos de preguntas (selección múltiple, explicación abierta y problema paso a paso) se mezclan en un orden aleatorio nuevo para cada intento.
5. Antes de empezar se informa que permanecer fuera de la autoevaluación más de 5 segundos reinicia el intento.
6. Si se regresa antes de superar los 5 segundos, se conserva el progreso y aparece un aviso informativo.
7. Si se regresa después de más de 5 segundos, el intento anterior se descarta, comienza uno nuevo en el mismo módulo y aparece un aviso visible de que se salió y se reinició.
8. La detección contempla cambio de pestaña, pérdida de foco confirmada y navegación/cierre de página.
9. No se envían eventos de salida, duración, copiado o pegado a docentes. No hay panel docente de monitoreo de estas actividades.

## Aplicar en el proyecto local

Desde la carpeta que contiene `manage.py`:

```bash
python -m venv .venv
```

En Git Bash:

```bash
source .venv/Scripts/activate
pip install -r requirements.txt
```

Configura `.env` (puedes copiar `.env.example` como base). Para desarrollo local con SQLite, usa al menos:

```env
SECRET_KEY=pon-aqui-una-clave-larga
NUMLEARN_DEBUG=True
DATABASE_URL=
ALLOW_SQLITE=True
```

Después ejecuta:

```bash
python manage.py migrate
python manage.py test
python manage.py runserver
```

Abre `http://127.0.0.1:8000/ecuaciones-no-lineales/autoevaluacion/`.

## Comprobación manual en navegador

- La pantalla inicial muestra opciones para Módulo 1, Módulo 2, curso completo y errores numéricos.
- La ruta del módulo 1 deja seleccionado el módulo completo, no solo errores numéricos.
- Antes de empezar se muestra el aviso de los cinco segundos.
- No aparece el tamaño del banco ni el total de preguntas.
- En varios intentos, los tipos «Conceptos», «Explicación» y «Problema paso a paso» aparecen en distinto orden.
- Cambia de pestaña y regresa antes de 5 segundos: aparece un aviso informativo y se conserva el avance.
- Cambia de pestaña y regresa después de 5 segundos: aparece un aviso de salida y el intento empieza desde la primera pregunta del mismo módulo.
- No aparece un panel docente ni se guarda un registro de salidas o duración.

## Verificación automatizada realizada

- `python manage.py test`: 168 pruebas aprobadas.
- `node --check static/js/assessment/assessment.js`: sintaxis JavaScript correcta.
- `python -m compileall`: sintaxis Python correcta.
- Las pruebas de Django confirman que el selector incluye ambos módulos y que la salida corta conserva el intento mientras la salida prolongada lo reinicia.
