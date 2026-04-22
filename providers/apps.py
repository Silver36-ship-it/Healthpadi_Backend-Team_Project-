from django.apps import AppConfig


class ProvidersConfig(AppConfig):
    name = 'providers'
    default_auto_field = 'django.db.models.BigAutoField'

    def ready(self):
        import providers.signals  # noqa: F401
