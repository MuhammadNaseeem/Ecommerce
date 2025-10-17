from django.urls import path
from . import views

app_name = "orders"

urlpatterns = [
    path("", views.orders_home, name="orders_home"),  # Optional root for /orders/
    path("checkout/", views.checkout, name="checkout"),
    path("create-checkout-session/", views.create_checkout_session, name="create_checkout_session"),
    path("success/", views.checkout_success, name="checkout_success"),
    path('confirmation/<int:order_id>/', views.order_confirmation, name='order_confirmation'),
    path('invoice/<int:order_id>/', views.generate_invoice_pdf, name='generate_invoice_pdf'),
    path('paypal/create/', views.create_paypal_payment, name='create_paypal_payment'),
    path('paypal/success/', views.paypal_success, name='paypal_success'),
]


