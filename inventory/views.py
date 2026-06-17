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
def stock_movements(request):
    movements = StockMovement.objects.all().select_related('product', 'user')

    # Filtre par produit
    product_id = request.GET.get('product', '')
    if product_id:
        movements = movements.filter(product_id=product_id)

    # Filtre par type
    movement_type = request.GET.get('type', '')
    if movement_type:
        movements = movements.filter(movement_type=movement_type)

    # Pagination
    paginator = Paginator(movements, 20)  # 20 mouvements par page
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    products = Product.objects.all()

    context = {
        'page_obj': page_obj,
        'products': products,
        'selected_product': product_id,
        'selected_type': movement_type,
    }

    return render(request, 'inventory/stock_movements.html', context)


@login_required
def export_stock_movements_csv(request):
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename="export_stock_movements_csv.csv"'

    writer = csv.writer(response, delimiter=';')

    writer.writerow([
        'Product',
        'SKU',
        'Movement Type',
        'Quantity',
        'Reason',
        'Date',
        'Time'
    ])

    movements = StockMovement.objects.select_related('product')

    if request.GET.get('product'):
        movements = movements.filter(product_id=request.GET['product'])

    if request.GET.get('type'):
        movements = movements.filter(movement_type=request.GET['type'])

    movements = movements.order_by('-created_at')

    for movement in movements:
        dt = localtime(movement.created_at)

        writer.writerow([
            movement.product.name,
            movement.product.sku,
            movement.get_movement_type_display(),
            movement.quantity,
            movement.reason or 'N/A',
            dt.strftime('%d/%m/%Y'),
            dt.strftime('%H:%M')
        ])

    return response


@login_required
def stock_movements_stats_api(request):
    """
    API JSON: total quantity IN / OUT per day
    """
    data = (
        StockMovement.objects
        .annotate(date=TruncDate('created_at'))
        .values('date', 'movement_type')
        .annotate(total=Sum('quantity'))
        .order_by('date')
    )

    return JsonResponse(list(data), safe=False)


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
