from django.urls import path
from .views import DashboardView, OrderHistoryView
from products.views import delete_order

urlpatterns = [
    path('dashboard/', DashboardView.as_view(), name='dashboard'),
    path('order/delete/<str:order_ref>/', delete_order, name='delete_order'),
    
     path('order-history/', OrderHistoryView.as_view(), name='order_history'),
    # ... other URL patterns ...
]