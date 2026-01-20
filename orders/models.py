from django.db import models
from goods.models import Goods  # твоя модель товаров

class Order(models.Model):
    DELIVERY_CHOICES = [
        ('pickup', 'Самовывоз'),
        ('delivery', 'Доставка'),
    ]

    phone_number = models.CharField("Телефон", max_length=20)
    address = models.TextField("Адрес", blank=True, null=True)
    delivery_type = models.CharField(
        "Способ получения",
        max_length=10,
        choices=DELIVERY_CHOICES,
        default='pickup'
    )
    is_done = models.BooleanField("Выполнена", default=False)
    created_at = models.DateTimeField("Время создания", auto_now_add=True)

    class Meta:
        verbose_name = "Заказ"
        verbose_name_plural = "Заказы"
        ordering = ['-created_at']

    def __str__(self):
        return f"Заказ #{self.id}"

    def get_delivery_type_display(self):
        return "Самовывоз" if self.delivery_type == "pickup" else "Доставка"

    @property
    def total_quantity(self):
        """Общее количество товаров в заказе"""
        return sum(item.quantity for item in self.items.all())

    @property
    def total_price(self):
        """Сумма всех товаров в заказе"""
        return sum(
            (item.quantity * item.price) if item.price else 0
            for item in self.items.all()
        )
    
    


class OrderItem(models.Model):
    order = models.ForeignKey(Order, related_name="items", on_delete=models.CASCADE)
    product = models.ForeignKey(Goods, on_delete=models.PROTECT)
    quantity = models.PositiveIntegerField(default=1)
    price = models.DecimalField("Цена на момент заказа", max_digits=10, decimal_places=2)

    class Meta:
        verbose_name = "Товар в заказе"
        verbose_name_plural = "Товары в заказе"

    def __str__(self):
        return f"{self.product.name} × {self.quantity}"

    @property
    def total_price(self):
        if self.price is None:
            return 0
        return self.quantity * self.price