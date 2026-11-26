"""Lecciones nuevas del temario, agrupadas por unidad. `LESSONS[slug]` devuelve el contenido de una lección.

Cada lección es un diccionario con: resumen, objetivos, idea central, fórmulas, algoritmo, ejercicio
resuelto, confusiones frecuentes, laboratorio (`lab.kind`, ver static/js/temario/labs.js) y preguntas
de comprobación. Los valores de los ejercicios resueltos se verifican en tests/temario-numeric.test.cjs.
"""
from . import unidad1, unidad2, unidad3, unidad4, unidad5, unidad6

LESSONS = {}
for _module in (unidad1, unidad2, unidad3, unidad4, unidad5, unidad6):
    for _lesson in _module.LESSONS:
        LESSONS[_lesson['slug']] = _lesson
