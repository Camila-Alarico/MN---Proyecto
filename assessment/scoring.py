"""Puntaje por unidad y puntaje acumulado del curso.

NO es el porcentaje de temas completados (ese es `temario.views.units_context` y solo mide recorrido).
Este puntaje sale únicamente de las autoevaluaciones terminadas y se calcula así:

* Puntaje de una unidad = el MEJOR intento terminado de la evaluación propia de esa unidad,
  `puntos / problemas × 100`. Cada problema vale entre 0 y 1 (promedio de sus etapas: 1, 0.5 o 0.25 puntos según
  el intento en que se acierta, 0 si hay que mostrar la respuesta).
* Puntaje acumulado = promedio simple (todas las unidades pesan igual) de los puntajes de las unidades evaluadas
  que el estudiante ya rindió.
* Una unidad sin evaluación disponible (hoy 2, 5, 6 y 7) no entra en la fórmula: no se le inventa un cero ni un
  puntaje. Una unidad con evaluación que aún no se rindió tampoco entra; se informa como pendiente.
* Las evaluaciones conjuntas (`modulo-1`, `curso`) abarcan varias unidades y no se cuentan, para no duplicar.
"""
from temario.catalog import UNITS
from temario.navigation import ASSESSMENTS

from .models import Attempt

SCOPE_TO_UNIT = {scope: number for number, (scope, _title, _coverage) in ASSESSMENTS.items()}


def _finished_attempts(user, session_key):
    attempts = Attempt.objects.filter(finished_at__isnull=False, points__isnull=False, total__gt=0,
                                      scope__in=SCOPE_TO_UNIT)
    if user is not None and getattr(user, 'is_authenticated', False):
        return attempts.filter(user=user)
    if not session_key:
        return attempts.none()
    return attempts.filter(session_key=session_key, user__isnull=True)


def course_score(user, session_key):
    """Devuelve `{'percent', 'taken', 'available', 'passed', 'pass_percent', 'units'}`.

    `percent` es None mientras no haya ninguna unidad rendida. `units` trae una fila por unidad del curso con
    `status` = `scored` (hay puntaje), `pending` (evaluación disponible, sin rendir) o `none` (sin evaluación).
    """
    from .engine import PASS_RATIO

    best = {}
    for attempt in _finished_attempts(user, session_key).only('scope', 'points', 'total', 'finished_at'):
        unit, ratio = SCOPE_TO_UNIT[attempt.scope], attempt.points / attempt.total
        if unit not in best or ratio > best[unit]['ratio']:
            best[unit] = {'ratio': ratio, 'points': attempt.points, 'total': attempt.total}
    rows = []
    for unit in UNITS:
        number = unit['number']
        row = {'number': number, 'title': unit['title']}
        if number not in ASSESSMENTS:
            row.update(status='none', percent=None)
        elif number in best:
            row.update(status='scored', percent=round(100 * best[number]['ratio']), points=best[number]['points'],
                       total=best[number]['total'], passed=best[number]['ratio'] >= PASS_RATIO)
        else:
            row.update(status='pending', percent=None)
        rows.append(row)
    scored = [row for row in rows if row['status'] == 'scored']
    percent = round(100 * sum(best[row['number']]['ratio'] for row in scored) / len(scored)) if scored else None
    return {'percent': percent, 'taken': len(scored), 'available': len(ASSESSMENTS), 'units': rows,
            'passed': None if percent is None else percent >= round(PASS_RATIO * 100),
            'pass_percent': round(PASS_RATIO * 100)}
