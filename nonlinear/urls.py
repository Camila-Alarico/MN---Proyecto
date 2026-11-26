"""Rutas de páginas del módulo 1 (ecuaciones no lineales).

CONVERGEN (varios orígenes -> un solo destino):
  * Sidebar, tarjetas del temario, buscador y enlaces de las lecciones -> `page` (`<slug>/`).
    Un tema o método tiene una única URL canónica, sin variantes.
  * Enlaces heredados `/laboratorio/?method=...` -> `legacy_lab`, que redirige 301 al `page`
    del método pedido conservando el resto de parámetros (marcadores, historial exportado).

Los índices heredados redirigen a la unidad del curso en `/`. La búsqueda global
vive en `core` y las prácticas aceptan `?tema=` para mostrar solo el tema elegido.
"""
from django.urls import path

from . import learning_views, views

app_name = 'nonlinear'
urlpatterns = [
    path('', views.landing, name='landing'),
    path('teoria/', learning_views.theory, name='theory'),
    path('practica/', learning_views.practice, name='practice'),
    path('autoevaluacion/', learning_views.assessment, name='assessment'),
    # Debe ir antes que `<slug>/` para que "laboratorio" no se trate como un tema.
    path('laboratorio/', views.legacy_lab, name='lab-legacy'),
    path('<slug:slug>/', views.page, name='page'),
]
