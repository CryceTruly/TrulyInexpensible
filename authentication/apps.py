from django.apps import AppConfig


class authenticationConfig(AppConfig):
    name = 'authentication'

    def ready(self):
        import profile.signals
