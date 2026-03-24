from django.db import models
from products.models import Product
from django.contrib.auth.models import User


class Stock(models.Model):
    product = models.OneToOneField(Product, on_delete=models.CASCADE)
    quantity = models.IntegerField(default=0)
    minimum_stock = models.IntegerField(default=10)
    last_updated = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.product.name} - {self.quantity} units"

    def is_low_stock(self):
        return self.quantity <= self.minimum_stock


class Order(models.Model):
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('shipped', 'Shipped'),
        ('delivered', 'Delivered'),
    ]

    order_number = models.CharField(max_length=50, unique=True)
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity = models.IntegerField()
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    order_date = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Order {self.order_number} - {self.status}"


class StockMovement(models.Model):
    MOVEMENT_TYPES = [
        ('in', 'Stock In'),
        ('out', 'Stock Out'),
        ('adjustment', 'Adjustment'),
    ]

    product = models.ForeignKey('products.Product', on_delete=models.CASCADE,related_name='movements')
    movement_type = models.CharField(max_length=20, choices=MOVEMENT_TYPES)
    quantity = models.IntegerField()
    previous_quantity = models.IntegerField()
    new_quantity = models.IntegerField()
    reason = models.CharField(max_length=200, blank=True)
    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.product.name} - {self.movement_type} - {self.quantity}"
