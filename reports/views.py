from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from inventory.models import Order
from django.db.models import Count, Sum

@login_required
def sales_report(request):
    orders = Order.objects.filter(status='delivered')
    total_sales = orders.count()
    return render(request, 'reports/sales_report.html', {
        'orders': orders,
        'total_sales': total_sales
    })

@login_required
def stock_report(request):
    from inventory.models import Stock
    stocks = Stock.objects.all().select_related('product')
    return render(request, 'reports/stock_report.html', {'stocks': stocks})
