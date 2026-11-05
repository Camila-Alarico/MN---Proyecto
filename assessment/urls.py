"""Rutas de la evaluación.

  /evaluacion/                  página para el alumno (alcance con ?alcance=errores|modulo-1|modulo-2|curso)
  /evaluacion/api/              API JSON (iniciar, reanudar, responder y reiniciar)
"""
from django.urls import path

from . import views

app_name = 'assessment'
urlpatterns = [
    path('', views.page, name='page'),
    path('api/', views.api, name='api'),
]
