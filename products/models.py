import math
from django.db import models
from django.utils import timezone
from datetime import timedelta
from django.utils.timezone import now


class Category(models.Model):
    name = models.CharField(max_length=100)
    description = models.TextField(blank=True)

    class Meta:
        verbose_name_plural = 'Categories'

    def __str__(self):
        return self.name


class Supplier(models.Model):
    name = models.CharField(max_length=200)
    email = models.EmailField()
    phone = models.CharField(max_length=15)
    address = models.TextField()

    def __str__(self):
        return self.name


class Product(models.Model):
    name = models.CharField(max_length=200)
    sku = models.CharField(max_length=50, unique=True)
    category = models.ForeignKey(Category, on_delete=models.SET_NULL, null=True)
    supplier = models.ForeignKey(Supplier, on_delete=models.SET_NULL, null=True)
    description = models.TextField(blank=True)
    unit_price = models.DecimalField(max_digits=10, decimal_places=2)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    cost_price = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        null=True,
        blank=True,
        help_text="Cost price per unit"
    )

    current_stock = models.IntegerField(
        default=0,
        help_text="Current quantity in inventory"
    )

    low_stock_threshold = models.IntegerField(
        default=10,
        help_text="Alert when stock falls below this level"
    )

    location = models.CharField(
        max_length=100,
        blank=True,
        null=True,
        help_text="Storage location"
    )

    barcode = models.CharField(
        max_length=50,
        blank=True,
        null=True,
        unique=True
    )

    is_active = models.BooleanField(default=True)

    image = models.ImageField(
        upload_to='products/',
        blank=True,
        null=True
    )

    def __str__(self):
        return self.name

    def get_stock_value(self):
        #Calculate total value of current stock
        if self.cost_price:
            return self.current_stock * self.cost_price
        return self.current_stock * self.unit_price

    def get_stock_status(self):
        #Get stock status
        if self.current_stock <= 0:
            return ('out_of_stock', 'Out of Stock', 'danger')
        elif self.current_stock <= self.low_stock_threshold:
            return ('low_stock', 'Low Stock', 'warning')
        else:
            return ('in_stock', 'In Stock', 'success')
def update_stock(self, quantity, movement_type='in', user=None, reason=''):
    """
    Update stock and create movement record.
    This method interacts with inventory.StockMovement
    """
    from inventory.models import StockMovement

    movement_type = movement_type.lower()

    if movement_type == 'out' and quantity > self.current_stock:
        raise ValueError(
            f"Insufficient stock for {self.name}. "
            f"Available: {self.current_stock}, Requested: {quantity}"
        )

    old_stock = self.current_stock

    if movement_type == 'in':
        self.current_stock += quantity
    elif movement_type == 'out':
        self.current_stock -= quantity
    elif movement_type == 'adjustment':
        self.current_stock = quantity
    else:
        raise ValueError(f"Invalid movement_type: {movement_type}")

    self.save()

    movement = StockMovement.objects.create(
        product=self,
        movement_type=movement_type,
        quantity=quantity,
        previous_quantity=old_stock,
        new_quantity=self.current_stock,
        reason=reason or f"Stock updated from {old_stock} to {self.current_stock}",
        user=user,
    )

    return {
        'movement': movement,
        'new_stock': self.current_stock,
        'old_stock': old_stock
    }


def get_total_in(self):
    """Get total quantity received"""
    from inventory.models import StockMovement
    from django.db.models import Sum
    return StockMovement.objects.filter(
        product=self,
        movement_type='in'
    ).aggregate(total=Sum('quantity'))['total'] or 0


def get_total_out(self):
    """Get total quantity sold/dispatched"""
    from inventory.models import StockMovement
    from django.db.models import Sum
    return StockMovement.objects.filter(
        product=self,
        movement_type='out'
    ).aggregate(total=Sum('quantity'))['total'] or 0


def get_stock_history(self, days=30):
    """Get stock movements for the last N days"""
    from inventory.models import StockMovement

    start_date = now() - timedelta(days=days)
    return StockMovement.objects.filter(
        product=self,
        created_at__gte=start_date
    ).order_by('-created_at')


    class Meta:
        ordering = ['name']
        indexes = [
            models.Index(fields=['sku']),
            models.Index(fields=['name']),
            models.Index(fields=['current_stock']),
        ]
