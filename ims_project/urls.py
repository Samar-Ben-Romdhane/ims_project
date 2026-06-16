urlpatterns = [
    path('admin/', admin.site.urls),
    path('accounts/', include('accounts.urls')),
    path('', include('inventory.urls', namespace='inventory_root')),
    path('products/', include('products.urls')),
    path('inventory/', include('inventory.urls')),
    path('reports/', include('reports.urls')),
    path('', include('django_prometheus.urls')),
    # optional: redirect root to dashboard
    #path('', RedirectView.as_view(url='/dashboard/')),

]
