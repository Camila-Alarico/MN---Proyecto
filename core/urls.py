"""Rutas globales del portal.

CONVERGEN: todas las búsquedas (barra superior, cualquier página) -> `search` (`/buscar/?q=`).
El destino no depende de dónde se escriba la consulta.
La portada es el único índice del curso. Los índices anteriores redirigen a ella;
las lecciones conservan sus URL canónicas y `/avance/` funciona también para invitados.
"""
from django.urls import path

from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('avance/', views.course_progress, name='course-progress'),
    path('empieza-aqui/', views.introduction, name='introduction'),
    path('teoria/', views.theory, name='theory-hub'),
    path('buscar/', views.search, name='search'),
    path('health/', views.health, name='health'),
    path('cuenta/registro/', views.register, name='register'),
    path('recursos/', views.resources, name='resources'),
    path('mi-progreso/', views.progress, name='progress'),
    path('mis-apuntes/', views.notes, name='notes'),
    path('mis-apuntes/<int:pk>/eliminar/', views.delete_note, name='delete-note'),
    path('favoritos/', views.favorites, name='favorites'),
    path('historial/<int:pk>/favorito/', views.toggle_favorite, name='toggle-favorite'),
    path('historial/<int:pk>/eliminar/', views.delete_history, name='delete-history'),
]
