from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import F
from .models import Stock, Order, StockMovement
from products.models import Product
from django.core.paginator import Paginator
from django.http import HttpResponse
import csv
from django.utils.timezone import localtime
from django.http import JsonResponse
from django.db.models import Sum
from django.db.models.functions import TruncDate
from .metrics import stock_movements_counter




@login_required
def stock_list(request):
    products = Product.objects.all().select_related('category', 'supplier')
    return render(request, 'inventory/stock_list.html', {'products': products})


@login_required
def stock_alert(request):
    low_stock_products = Product.objects.filter(current_stock__lte=F('low_stock_threshold'))
    return render(request, 'inventory/stock_alert.html', {'low_stock_products': low_stock_products})


@login_required
def add_stock_movement(request):
    if request.method == 'POST':
        product_id = request.POST.get('product')
        movement_type = request.POST.get('movement_type')
        quantity = int(request.POST.get('quantity'))
        reason = request.POST.get('reason', '')

        product = get_object_or_404(Product, pk=product_id)
        previous_qty = product.current_stock

        if movement_type == 'out' and quantity > product.current_stock:
            messages.error(request, f"Stock insuffisant pour {product.name}. Disponible : {product.current_stock}")
            return redirect('inventory:add_movement')

        if movement_type == 'in':
            product.current_stock = F('current_stock') + quantity
        else:  # out ou adjustment
            product.current_stock = F('current_stock') - quantity

        product.save()
        product.refresh_from_db()

        movement = StockMovement.objects.create(
            product=product,
            movement_type=movement_type,
            quantity=quantity,
            previous_quantity=previous_qty,
            new_quantity=product.current_stock,
            reason=reason,
            user=request.user
        )

        stock_movements_counter.labels(movement_type=movement.movement_type).inc(movement.quantity)
        messages.success(request, 'Stock movement recorded successfully!')
        return redirect('inventory:movements')

    products = Product.objects.all()
    return render(request, 'inventory/add_movement.html', {'products': products})
