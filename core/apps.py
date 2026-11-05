from django.apps import AppConfig


class CoreConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'core'
    verbose_name = 'NumLearn: cuentas y progreso'

    def ready(self):
        from . import signals  # noqa: F401  (registra la señal user_logged_in)
