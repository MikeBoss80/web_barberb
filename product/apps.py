from django.apps import AppConfig


class ProductConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'product'
    verbose_name = 'Gestión de Productos'
    
    def ready(self):
        # Importar señales si las hay
        try:
            import product.signals
        except ImportError:
            pass
