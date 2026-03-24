from django.urls import path
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
