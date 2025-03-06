# signals.py

from django.db.models.signals import post_save
from django.dispatch import receiver
from django.core.exceptions import ValidationError
from .models import OrderItem, Product


# Сигнал, который уменьшает количество товара в момент создания элемента заказа
@receiver(post_save, sender=OrderItem)
def update_product_quantity(sender, instance, created, **kwargs):
    if created:  # Сигнал срабатывает только при создании нового OrderItem
        product = instance.product
        quantity_ordered = instance.amount

        if product.quantity >= quantity_ordered:
            # Уменьшаем количество продукта на складе
            product.quantity -= quantity_ordered
            product.save()  # Сохраняем обновленное количество
        else:
            # Если на складе недостаточно товара, выбрасываем исключение
            raise ValidationError(
                f"Not enough stock for {product.name}. Available: {product.quantity}, Ordered: {quantity_ordered}")
