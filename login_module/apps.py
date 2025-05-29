from django.apps import AppConfig


class LoginModuleConfig(AppConfig):
    name = 'login_module'

    def ready(self):
        import login_module.signals