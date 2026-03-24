from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.db.models import F, Sum, Count
from django.db.models.functions import TruncDate
from products.models import Product
from inventory.models import Stock, Order, StockMovement
from datetime import datetime, timedelta
import json


@login_required
def dashboard_home(request):
    total_products = Product.objects.count()
    low_stock_count = Stock.objects.filter(quantity__lte=F('minimum_stock')).count()
    pending_orders = Order.objects.filter(status='pending').count()
    recent_orders = Order.objects.all().order_by('-order_date')[:5]

    # Données pour graphiques - Ventes des 7 derniers jours
    seven_days_ago = datetime.now() - timedelta(days=7)
    daily_orders = Order.objects.filter(
        order_date__gte=seven_days_ago
    ).annotate(
        date=TruncDate('order_date')
    ).values('date').annotate(
        count=Count('id')
    ).order_by('date')

    # Préparer les données pour Chart.js
    dates = [item['date'].strftime('%Y-%m-%d') for item in daily_orders]
    counts = [item['count'] for item in daily_orders]

    # Top 5 produits les plus commandés
    top_products = Order.objects.values(
        'product__name'
    ).annotate(
        total_quantity=Sum('quantity')
    ).order_by('-total_quantity')[:5]

    product_names = [item['product__name'] for item in top_products]
    product_quantities = [item['total_quantity'] for item in top_products]

    # Mouvements de stock récents
    recent_movements = StockMovement.objects.all().select_related('product', 'user')[:10]

    context = {
        'total_products': total_products,
        'low_stock_count': low_stock_count,
        'pending_orders': pending_orders,
        'recent_orders': recent_orders,
        'recent_movements': recent_movements,
        'chart_dates': json.dumps(dates),
        'chart_counts': json.dumps(counts),
        'product_names': json.dumps(product_names),
        'product_quantities': json.dumps(product_quantities),
    }
    return render(request, 'dashboard/dashboard.html', context)
