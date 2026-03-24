from prometheus_client import Counter

stock_movements_counter = Counter(
    'stock_movements_total',
    'Total stock movements',
    ['movement_type']
)
