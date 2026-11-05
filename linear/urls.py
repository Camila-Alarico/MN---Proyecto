"""Rutas de páginas del módulo 2 (sistemas de ecuaciones lineales). Misma forma que nonlinear/urls.py.

Un contenido = una URL canónica `<slug>/`. `legacy_lab` (`laboratorio/?method=...`) redirige 301
al `page` del método pedido. Las rutas fijas van antes de `<slug>/`.
"""
from django.urls import path

from . import views

app_name = 'linear'
urlpatterns = [
    path('', views.landing, name='landing'),
    path('laboratorio/', views.legacy_lab, name='lab-legacy'),
    path('<slug:slug>/', views.page, name='page'),
]
