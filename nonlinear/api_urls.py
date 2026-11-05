"""API JSON del módulo 1. El orden importa: las rutas fijas van antes de `<slug:method>/`."""
from django.urls import path

from . import learning_views, views

urlpatterns = [
    path('learning/<slug:mode>/', learning_views.activity),
    path('graph/', views.graph),
    path('errors/', views.errors),
    path('compare/', views.compare),  # recorridos, error y propagación (comparar.html)
    path('progress/', views.complete_topic),
    path('<slug:method>/', views.solve),
]
