"""Destinos del curso: actividades disponibles y alcance real de cada evaluación."""
from django.urls import reverse

ASSESSMENTS = {
    
    1: ('errores', 'Evaluar errores numéricos', 'Evalúa medidas de error, origen y tolerancia.'),
    2: ('unidad-2-aproximacion', 'Evaluar aproximación', 'Taylor, truncamiento, redondeo y exactitud.'),
    3: ('unidad-2', 'Evaluar raíces de ecuaciones', 'Bisección, regla falsa, punto fijo, Newton, secante y raíces múltiples.'),
    4: ('modulo-2', 'Evaluar sistemas lineales', 'Formulación, Gauss, Gauss-Seidel y comparación.'),
    5: ('unidad-5', 'Evaluar ajuste de curvas', 'Ajuste lineal e interpolación.'),
    6: ('unidad-6', 'Evaluar integración y derivación', 'Regla trapezoidal y diferencia central.'),
    7: ('unidad-7', 'Evaluar ecuaciones diferenciales', 'Euler y Euler modificado.'),
}


def assessment_for(unit_number):
    item = ASSESSMENTS.get(unit_number)
    if not item:
        return None
    scope, title, coverage = item
    return {'url': f"{reverse('assessment:page')}?alcance={scope}", 'title': title, 'coverage': coverage}
