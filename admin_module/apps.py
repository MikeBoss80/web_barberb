from django.apps import AppConfig


class AdminModuleConfig(AppConfig):
    name = 'admin_module'

    def ready(self):
        import admin_module.signals