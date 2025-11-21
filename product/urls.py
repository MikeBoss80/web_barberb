from django.urls import path
from . import views

app_name = 'product'

urlpatterns = [
    # Productos
    path('', views.ProductListView.as_view(), name='product_list'),
    path('product/<int:pk>/', views.ProductDetailView.as_view(), name='product_detail'),
    path('product/create/', views.ProductCreateView.as_view(), name='product_create'),
    path('product/<int:pk>/edit/', views.ProductUpdateView.as_view(), name='product_edit'),
    path('product/<int:pk>/delete/', views.ProductDeleteView.as_view(), name='product_delete'),
    
    # Categorías
    path('categories/', views.CategoryListView.as_view(), name='category_list'),
    path('categories/create/', views.CategoryCreateView.as_view(), name='category_create'),
    
    # Movimientos de inventario
    path('movements/', views.StockMovementListView.as_view(), name='stock_movement_list'),
    path('movements/create/', views.StockMovementCreateView.as_view(), name='stock_movement_create'),
    path('stock/adjust/', views.QuickStockAdjustmentView.as_view(), name='quick_stock_adjustment'),
    
    # Reportes
    path('reports/low-stock/', views.LowStockReportView.as_view(), name='low_stock_report'),
    
    # AJAX endpoints
    path('ajax/stock/<int:product_id>/<int:establishment_id>/', 
         views.GetProductStockAjaxView.as_view(), name='get_product_stock_ajax'),
]