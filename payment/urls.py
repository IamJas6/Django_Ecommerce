from django.urls import path
from . import views

urlpatterns = [
    path('shippingaddress', views.shippingaddress, name='shippingaddress'),
    path('checkout', views.checkout, name='checkout'),
    path('billing_info', views.billing_info, name='billing_info'),
    path('process_order', views.process_order, name='process_order'),
    path('shipped_page', views.shipped_page, name='shipped_page'),
    path('unshipped_page', views.unshipped_page, name='unshipped_page'),
    path('orders/<int:pk>', views.orders, name='orders'),
]