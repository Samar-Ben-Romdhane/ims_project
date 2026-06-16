"""
URL configuration for ims_project project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/dev/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include
from django.views.generic import RedirectView


urlpatterns = [
    path('admin/', admin.site.urls),
    path('accounts/', include('accounts.urls')),
    path('', include('inventory.urls')),
    path('products/', include('products.urls')),
    path('inventory/', include('inventory.urls')),
    path('reports/', include('reports.urls')),
    path('', include('django_prometheus.urls')),
    # optional: redirect root to dashboard
    #path('', RedirectView.as_view(url='/dashboard/')),

]from django.urls import path
from . import views

app_name = 'inventory'

urlpatterns = [
    path('', views.stock_movements, name='home'),  # HOME → movements
    path('stock/', views.stock_list, name='stock_list'),
    path('alerts/', views.stock_alert, name='alerts'),
    path('movements/', views.stock_movements, name='movements'),
    path('movements/add/', views.add_stock_movement, name='add_movement'),
    path('movements/export/csv/', views.export_stock_movements_csv, name='export_movements_csv'),
    path('api/movements/stats/', views.stock_movements_stats_api, name='movements_stats_api'),


]
