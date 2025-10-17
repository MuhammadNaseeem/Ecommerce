from django.shortcuts import render, redirect
from django.core.mail import send_mail
from django.contrib import messages
from django.conf import settings
from django.views.generic import TemplateView, ListView, CreateView, UpdateView
from django.urls import reverse_lazy
from django.contrib.auth import get_user_model
from .models import Product, Category, Order, Coupon

# Get the correct User model (custom or default)
User = get_user_model()

# ----------------------------
# Home Page
# ----------------------------
def home(request):
    products = Product.objects.filter(available=True).order_by('-created_at')[:8]
    return render(request, "core/home.html", {"products": products})

# ----------------------------
# Contact Page
# ----------------------------
def contact(request):
    if request.method == "POST":
        name = request.POST.get("name")
        email = request.POST.get("email")
        subject = request.POST.get("subject")
        message = request.POST.get("message")

        if name and email and subject and message:
            full_message = f"From: {name} <{email}>\n\n{message}"
            try:
                send_mail(
                    subject,
                    full_message,
                    settings.DEFAULT_FROM_EMAIL,
                    [settings.DEFAULT_FROM_EMAIL],
                    fail_silently=False,
                )
                messages.success(request, "Your message has been sent successfully!")
            except Exception as e:
                messages.error(request, f"There was an error sending your message: {e}")
        else:
            messages.error(request, "Please fill in all fields.")

    return render(request, "core/contact.html")

# ----------------------------
# Admin Dashboard Overview
# ----------------------------
class AdminDashboardView(TemplateView):
    template_name = "admin/dashboard.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['total_sales'] = Order.objects.filter(status='delivered').count()
        context['total_revenue'] = sum(o.total_price for o in Order.objects.filter(status='delivered'))
        context['total_customers'] = User.objects.count()
        context['low_stock'] = Product.objects.filter(stock__lte=5)
        return context

# ----------------------------
# Products
# ----------------------------
class ProductListView(ListView):
    model = Product
    template_name = "admin/products_list.html"

class ProductCreateView(CreateView):
    model = Product
    fields = ['name', 'category', 'price', 'stock', 'description']
    template_name = "admin/product_form.html"
    success_url = reverse_lazy('core:products_list')

class ProductUpdateView(UpdateView):
    model = Product
    fields = ['name', 'category', 'price', 'stock', 'description']
    template_name = "admin/product_form.html"
    success_url = reverse_lazy('core:products_list')

# ----------------------------
# Orders
# ----------------------------
class OrderListView(ListView):
    model = Order
    template_name = "admin/orders_list.html"

class OrderUpdateStatusView(UpdateView):
    model = Order
    fields = ['status']
    template_name = "admin/order_update.html"
    success_url = reverse_lazy('core:orders_list')

# ----------------------------
# Coupons
# ----------------------------
class CouponListView(ListView):
    model = Coupon
    template_name = "admin/coupons_list.html"

class CouponCreateView(CreateView):
    model = Coupon
    fields = ['code', 'discount', 'active', 'expiry_date']
    template_name = "admin/coupon_form.html"
    success_url = reverse_lazy('core:coupons_list')

class CouponUpdateView(UpdateView):
    model = Coupon
    fields = ['code', 'discount', 'active', 'expiry_date']
    template_name = "admin/coupon_form.html"
    success_url = reverse_lazy('core:coupons_list')

# ----------------------------
# Customers
# ----------------------------
class CustomerListView(ListView):
    model = User
    template_name = "admin/customers_list.html"



# naseem.9423!



# https://myaccount.google.com
# https://myaccount.google.com/apppasswords
