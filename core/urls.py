from django.urls import path
from . import views
from .views import (
    AdminDashboardView, ProductListView, ProductCreateView, ProductUpdateView,
    OrderListView, OrderUpdateStatusView, CouponListView, CouponCreateView,
    CouponUpdateView, CustomerListView
)

app_name = "core"

urlpatterns = [
    path("", views.home, name="home"),
    path("contact/", views.contact, name="contact"),  # Added Contact page

# Admin Dashboard
path('dashboard/', AdminDashboardView.as_view(), name='dashboard'),

# Products
path('products/', ProductListView.as_view(), name='products_list'),
path('products/add/', ProductCreateView.as_view(), name='product_add'),
path('products/<int:pk>/edit/', ProductUpdateView.as_view(), name='product_edit'),

# Orders
path('orders/', OrderListView.as_view(), name='orders_list'),
path('orders/<int:pk>/update/', OrderUpdateStatusView.as_view(), name='order_update'),

# Coupons
path('coupons/', CouponListView.as_view(), name='coupons_list'),
path('coupons/add/', CouponCreateView.as_view(), name='coupon_add'),
path('coupons/<int:pk>/edit/', CouponUpdateView.as_view(), name='coupon_edit'),

# Customers
path('customers/', CustomerListView.as_view(), name='customers_list'),

]


