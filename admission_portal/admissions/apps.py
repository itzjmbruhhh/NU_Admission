from django.apps import AppConfig


class AdmissionsConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'admissions'

    def ready(self):
        # Import signals to ensure enrollment_chance auto-scales
        from . import signals  # noqa: F401
