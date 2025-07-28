from django.db import models
import uuid

class Item(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(verbose_name="Item's name", max_length=256, blank=False)
    description = models.TextField(verbose_name="Item's description", max_length=4096, blank=False)
    price = models.DecimalField(verbose_name="Item's price", max_digits=10, decimal_places=2, blank=False)

    def __str__(self) -> str:
        return self.name

