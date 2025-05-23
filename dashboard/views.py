# from datetime import timedelta
from django.shortcuts import render
from django.views import View
from products.models import Order
from django.db.models import Sum

class DashboardView(View):
    def get(self, request, *args, **kwargs):
        # Fetch all orders for the current user
        orders = Order.objects.filter(user=request.user).order_by('-order_date')
        
        # Prepare order details for the template
        order_data = []
        for order in orders:
            order_data.append({
                'id': order.order_ref,
                'date': order.order_date.strftime('%Y-%m-%d'),
                'status': order.order_status,
                'payment_status': order.payment_status,
                # 'estimated_delivery' : order.order_date + timedelta(days=20),
                'amount': order.total_amount,
                'order_items': [
                    {
                        'product_name': item.product.name,
                        'quantity': item.quantity,
                        'color': item.color,
                        'size': item.size,
                        'price': item.total_price(),
                        'image': item.product.images.first().image.url if item.product.images.exists() else None
                    } for item in order.order_items.all()
                ],
                'shipping': {
                    'address': order.shipping_address,
                    'city': order.city,
                    'postal_code': order.postal_code,
                },
                'payment': {
                    'method': order.payment_method,
                    'transaction_id': order.transaction_id,
                    'status': order.payment_status,
                }
            })
        
        context = {
            'orders': order_data,
            'total_orders': orders.count(),
            'pending_orders': orders.filter(order_status='pending').count(),
            'completed_orders': orders.filter(order_status='completed').count(),
            'total_spent': orders.aggregate(total=Sum('total_amount'))['total'] or 0,
        }
        
        return render(request, 'dashboard/dashboard.html', context)
    

class OrderHistoryView(View):
    template_name = 'dashboard/order_history.html'
    
    def get(self, request, *args, **kwargs):
        orders = Order.objects.filter(user=request.user).order_by('-order_date')
        
        order_data = []
        for order in orders:
            order_data.append({
                'id': order.order_ref,
                'date': order.order_date.strftime('%Y-%m-%d'),
                'status': order.order_status,
                'payment_status': order.payment_status,
                'amount': order.total_amount,
                'order_items': [
                    {
                        'product_name': item.product.name,
                        'quantity': item.quantity,
                        'color': item.color,
                        'size': item.size,
                        'price': item.total_price(),
                        'image': item.product.images.first().image.url if item.product.images.exists() else None
                    } for item in order.order_items.all()
                ],
                'shipping': {
                    'address': order.shipping_address,
                    'city': order.city,
                    'postal_code': order.postal_code,
                },
                'payment': {
                    'method': order.payment_method,
                    'transaction_id': order.transaction_id,
                    'status': order.payment_status,
                }
            })
        
        context = {
            'orders': order_data,
        }
        
        return render(request, self.template_name, context)