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

    def update_stock(self, quantity, movement_type='IN', user=None, notes='', **kwargs):

        #Update stock and create movement record.
        #This method interacts with inventory.StockMovement

        from inventory.models import StockMovement  # Import from inventory app

        # Validate stock for "out" movements
        if movement_type == 'OUT' and quantity > self.current_stock:
            raise ValueError(
                f"Insufficient stock for {self.name}. "
                f"Available: {self.current_stock}, Requested: {quantity}"
            )

            # Update product stock
            old_stock = self.current_stock

            if movement_type == 'IN':
                self.current_stock += quantity
            elif movement_type == 'OUT':
                self.current_stock -= quantity
            elif movement_type == 'ADJUST':
                self.current_stock = quantity
            elif movement_type == 'RETURN':
                self.current_stock += quantity

            self.save()

            # Create stock movement record in inventory app
            movement = StockMovement.objects.create(
                product=self,
                movement_type=movement_type,
                quantity=quantity,
                user=user,
                notes=notes or f"Stock updated from {old_stock} to {self.current_stock}",
                unit_cost=self.cost_price or self.unit_price,
                # Pass any additional kwargs to StockMovement
                **kwargs
            )

            return {
                'movement': movement,
                'new_stock': self.current_stock,
                'old_stock': old_stock
            }

    def get_total_in(self):
        """Get total quantity received"""
        # Assurez-vous que StockMovement a un related_name vers Product
        # Sinon, modifiez 'stock_movements' selon votre configuration
        from inventory.models import StockMovement
        return StockMovement.objects.filter(
            product=self,
            movement_type='IN'
        ).aggregate(total=math.fsum('quantity'))['total'] or 0

    def get_total_out(self):
        """Get total quantity sold/dispatched"""
        from inventory.models import StockMovement
        return StockMovement.objects.filter(
            product=self,
            movement_type='OUT'
        ).aggregate(total=math.fsum('quantity'))['total'] or 0

    def get_recent_movements(self, limit=10):
        """Get recent stock movements from inventory app"""
        from inventory.models import StockMovement
        return StockMovement.objects.filter(
            product=self
        ).order_by('-created_at')[:limit]

    @property
    def stock_movements(self):
        """Property to access stock movements easily"""
        from inventory.models import StockMovement
        return StockMovement.objects.filter(product=self)

    def check_low_stock(self):
        #Check if stock is below threshold
        return self.current_stock <= self.low_stock_threshold

    @property
    def margin(self):
        #Calculate profit margin percentage
        if self.cost_price and self.unit_price > 0:
            return round(((self.unit_price - self.cost_price) / self.unit_price) * 100,2)
        return 0

    @property
    def profit_per_unit(self):
        """Calculate profit per unit"""
        if self.cost_price:
            return self.unit_price - self.cost_price
        return self.unit_price

    def get_stock_history(self, days=30):
        """Get stock movements for the last N days"""
        from inventory.models import StockMovement

        start_date = now() - timedelta(days=days)
        return StockMovement.objects.filter(
            product=self,
            date__gte=start_date
        ).order_by('-created_at')


    class Meta:
        ordering = ['name']
        indexes = [
            models.Index(fields=['sku']),
            models.Index(fields=['name']),
            models.Index(fields=['current_stock']),
        ]
