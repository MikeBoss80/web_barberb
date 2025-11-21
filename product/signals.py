"""
Señales para el módulo de productos
"""
from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
from .models import StockMovement, ProductEstablishment
from .utils.inventory import InventoryManager


@receiver(post_save, sender=StockMovement)
def update_stock_on_movement_save(sender, instance, created, **kwargs):
    """
    Actualiza el stock cuando se crea o modifica un movimiento
    """
    if created:  # Solo cuando se crea un nuevo movimiento
        InventoryManager.update_establishment_stock(
            instance.product, 
            instance.establishment
        )


@receiver(post_delete, sender=StockMovement)
def update_stock_on_movement_delete(sender, instance, **kwargs):
    """
    Actualiza el stock cuando se elimina un movimiento
    """
    InventoryManager.update_establishment_stock(
        instance.product, 
        instance.establishment
    )