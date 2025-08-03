from django.db import models
import uuid
from decimal import Decimal
from typing import TYPE_CHECKING, Dict

if TYPE_CHECKING:
    from .models import Item, OrderItem

class Item(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(verbose_name="Item's name", max_length=256, blank=False)
    description = models.TextField(verbose_name="Item's description", max_length=4096, blank=False)
    price = models.DecimalField(verbose_name="Item's price", max_digits=10, decimal_places=2, blank=False)
    currency = models.CharField(verbose_name="Currency", max_length=3, default="USD", blank=False)

    def __str__(self) -> str:
        return self.name


class Discount(models.Model):
    percentage = models.DecimalField(max_digits=5, decimal_places=2, verbose_name="Discount Percentage")
    code = models.CharField(max_length=50, unique=True, verbose_name="Discount Code", default="")

    def __str__(self):
        return f"{self.code} ({self.percentage}%)"


class Tax(models.Model):
    name = models.CharField(max_length=255, verbose_name="Tax Name")
    percentage = models.DecimalField(max_digits=5, decimal_places=2, verbose_name="Tax Percentage")

    def __str__(self):
        return f"{self.name} ({self.percentage}%)"


class Order(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    total_price = models.DecimalField(max_digits=10, decimal_places=2, default=Decimal("0.00"), blank=False, null=False)
    created_at = models.DateTimeField(auto_now_add=True)
    discount = models.ForeignKey(Discount, on_delete=models.SET_NULL, null=True, blank=True, related_name="orders")
    tax = models.ForeignKey(Tax, on_delete=models.SET_NULL, null=True, blank=True, related_name="orders")

    def apply_discount_code(self, code: str) -> bool:
        try:
            discount = Discount.objects.get(code=code)
            self.discount = discount
            self.calculate_total_price()
            return True
        except Discount.DoesNotExist:
            return False

    def calculate_total_price(self) -> None:
        subtotal = sum(order_item.item.price * order_item.quantity for order_item in self.order_items.all())
        discount_amount = (subtotal * self.discount.percentage / 100) if self.discount else Decimal("0.00")
        tax_amount = ((subtotal - discount_amount) * self.tax.percentage / 100) if self.tax else Decimal("0.00")
        self.total_price = subtotal - discount_amount + tax_amount
        self.save()

    def __str__(self) -> str:
        return f"Order {self.id} for {self.total_price}"


class OrderItem(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name="order_items")
    item = models.ForeignKey(Item, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField(default=1)

    def __str__(self):
        return f"{self.quantity} x {self.item.name} in Order {self.order.id}"

