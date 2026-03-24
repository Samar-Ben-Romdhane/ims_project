from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .models import Product, Category, Supplier
from django.http import HttpResponse
import math
import csv
# Import from inventory
from inventory.models import StockMovement
from decimal import Decimal



@login_required
def product_list(request):
    products = Product.objects.all().select_related('category', 'supplier')

    # --- GET parameters ---
    search_query = request.GET.get('search', '')
    selected_category = request.GET.get('category', '')
    selected_supplier = request.GET.get('supplier', '')
    current_sort = request.GET.get('sort', '-created_at')

    # --- Search ---
    if search_query:
        products = (products.filter(
            name__icontains=search_query) |
                    products.filter(sku__icontains=search_query)
                    )

    # --- Category filter ---
    if selected_category:
        products = products.filter(category_id=selected_category)

    # --- Supplier filter ---
    if selected_supplier:
        products = products.filter(supplier_id=selected_supplier)

    # --- Sorting ---
    allowed_sorts = [
        'created_at', '-created_at',
        'name', '-name',
        'unit_price', '-unit_price'
    ]
    if current_sort in allowed_sorts:
        products = products.order_by(current_sort)

    categories = Category.objects.all()
    suppliers = Supplier.objects.all()

    context = {
        'products': products,
        'categories': categories,
        'suppliers': suppliers,
        'search_query': search_query,
        'selected_category': selected_category,
        'selected_supplier': selected_supplier,
        'current_sort': current_sort,
    }

    return render(request, 'products/product_list.html', context)




@login_required
def product_create(request):
    if request.method == 'POST':
        name = request.POST.get('name')
        sku = request.POST.get('sku')
        category_id = request.POST.get('category')
        supplier_id = request.POST.get('supplier')
        unit_price = request.POST.get('unit_price')
        description = request.POST.get('description', '')

        Product.objects.create(
            name=name,
            sku=sku,
            category_id=category_id,
            supplier_id=supplier_id,
            unit_price=unit_price,
            description=description
        )
        messages.success(request, 'Product created successfully!')
        return redirect('products:list')

    categories = Category.objects.all()
    suppliers = Supplier.objects.all()
    return render(request, 'products/product_form.html', {
        'categories': categories,
        'suppliers': suppliers,
        'action': 'Create'
    })


@login_required
def product_update(request, pk):
    product = get_object_or_404(Product, pk=pk)

    if request.method == 'POST':
        product.name = request.POST.get('name')
        product.sku = request.POST.get('sku')
        product.category_id = request.POST.get('category')
        product.supplier_id = request.POST.get('supplier')
        product.unit_price = request.POST.get('unit_price')
        product.description = request.POST.get('description', '')
        product.save()

        messages.success(request, 'Product updated successfully!')
        return redirect('products:list')

    categories = Category.objects.all()
    suppliers = Supplier.objects.all()
    return render(request, 'products/product_form.html', {
        'product': product,
        'categories': categories,
        'suppliers': suppliers,
        'action': 'Update'
    })


@login_required
def product_delete(request, pk):
    """Delete a product"""
    product = get_object_or_404(Product, pk=pk)

    if request.method == 'POST':
        product_name = product.name
        product.delete()
        messages.success(request, f'Product "{product_name}" has been deleted.')
        return redirect('products:list')

    # If GET request, show confirmation page
    return render(request, 'products/product_confirm_delete.html', {
        'product': product
    })


@login_required
def export_products_csv(request):
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename="products_export.csv"'

    # ⚠️ delimiter=';' pour Excel FR
    writer = csv.writer(response, delimiter=';')
    writer.writerow([
        'SKU',
        'Name',
        'Category',
        'Supplier',
        'Unit Price($)',
        'Created At'
    ])

    # Base queryset
    products = Product.objects.all().select_related('category', 'supplier')

    # --- GET parameters ---
    search = request.GET.get('search', '').strip()
    category = request.GET.get('category', '')
    supplier = request.GET.get('supplier', '')
    sort = request.GET.get('sort', '-created_at')

    # --- Search (name OR sku) ---
    if search:
        products = products.filter(
            name__icontains=search
        ) | products.filter(
            sku__icontains=search
        )

    # --- Category filter ---
    if category:
        products = products.filter(category_id=category)

    # --- Supplier filter ---
    if supplier:
        products = products.filter(supplier_id=supplier)

    # --- Sorting (security) ---
    allowed_sorts = [
        'created_at', '-created_at',
        'name', '-name',
        'unit_price', '-unit_price'
    ]

    if sort in allowed_sorts:
        products = products.order_by(sort)

    # --- CSV rows ---
    for product in products:
        writer.writerow([
            product.sku,
            product.name,
            product.category.name if product.category else '',
            product.supplier.name if product.supplier else '',
            product.unit_price,
            product.created_at.strftime('%Y-%m-%d %H:%M:%S')
        ])

    return response

@login_required
def product_detail(request, pk):
    product = get_object_or_404(Product, pk=pk)

    # Gestion sécurisée des mouvements de stock
    try:
        from inventory.models import StockMovement

        stock_movements = StockMovement.objects.filter(
            product=product
        ).order_by('-created_at')[:10]

        # Calculs sécurisés
        try:
            total_in_result = StockMovement.objects.filter(
                product=product,
                movement_type='IN'
            ).aggregate(total=math.fsum('quantity'))
            total_in = total_in_result['total'] or 0
        except:
            total_in = 0

        try:
            total_out_result = StockMovement.objects.filter(
                product=product,
                movement_type='OUT'
            ).aggregate(total=math.fsum('quantity'))
            total_out = total_out_result['total'] or 0
        except:
            total_out = 0

    except (ImportError, Exception) as e:
        stock_movements = []
        total_in = 0
        total_out = 0
        print(f"Error loading stock movements: {e}")  # Pour le débogage

    context = {
        'product': product,
        'stock_movements': stock_movements,
        'total_in': total_in,
        'total_out': total_out,
        'net_movement': total_in - total_out,
    }

    return render(request, 'products/product_detail.html', context)
