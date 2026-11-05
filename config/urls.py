from django.contrib import admin
from django.contrib.auth import views as auth_views
from django.urls import include, path

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('core.urls')),
    path('ecuaciones-no-lineales/', include('nonlinear.urls')),
    path('api/nonlinear/', include('nonlinear.api_urls')),
    path('sistemas-lineales/', include('linear.urls')),
    path('evaluacion/', include('assessment.urls')),
    path('api/linear/', include('linear.api_urls')),
    # Cuentas
    path('cuenta/login/', auth_views.LoginView.as_view(), name='login'),
    path('cuenta/logout/', auth_views.LogoutView.as_view(), name='logout'),
    # Recuperación de contraseña (vistas estándar de Django, plantillas en templates/registration/)
    path('cuenta/recuperar/', auth_views.PasswordResetView.as_view(), name='password_reset'),
    path('cuenta/recuperar/enviado/', auth_views.PasswordResetDoneView.as_view(), name='password_reset_done'),
    path(
        'cuenta/recuperar/<uidb64>/<token>/',
        auth_views.PasswordResetConfirmView.as_view(),
        name='password_reset_confirm',
    ),
    path('cuenta/recuperar/listo/', auth_views.PasswordResetCompleteView.as_view(), name='password_reset_complete'),
]
