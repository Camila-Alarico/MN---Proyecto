"""API JSON del módulo 2. Las rutas fijas van antes de `<slug:method>/`."""
from django.urls import path

from . import views

urlpatterns = [
    path('compare/', views.compare),
    path('progress/', views.complete_topic),
    path('<slug:method>/', views.solve),
]
