"""Rutas del temario. `progreso/` va antes de `<slug>/` para que no se trate como una lección."""
from django.urls import path

from . import views

app_name = 'temario'
urlpatterns = [
    path('', views.index, name='index'),
    path('progreso/', views.progress, name='progress'),
    path('<slug:slug>/', views.lesson, name='lesson'),
]
