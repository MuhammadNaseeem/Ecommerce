from django.shortcuts import render
from products.models import Product

def home(request):
    # Get only available products, order newest first, limit to 8 featured items
    products = Product.objects.filter(available=True).order_by('-created_at')[:8]
    return render(request, "core/home.html", {"products": products})


from django.shortcuts import render
from django.core.mail import send_mail
from django.contrib import messages
from django.conf import settings

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
                    settings.DEFAULT_FROM_EMAIL,  # ✅ use your Gmail
                    [settings.DEFAULT_FROM_EMAIL],  # ✅ send to your Gmail
                    fail_silently=False,
                )
                messages.success(request, "Your message has been sent successfully!")
            except Exception as e:
                messages.error(request, f"There was an error sending your message: {e}")
        else:
            messages.error(request, "Please fill in all fields.")

    return render(request, "core/contact.html")

from django.shortcuts import render, redirect
from django.views.generic import TemplateView, ListView, CreateView, UpdateView
from django.urls import reverse_lazy
from django.contrib.auth import get_user_model
from .models import Product, Category, Order, Coupon

# Get the correct User model (custom or default)
User = get_user_model()

# Dashboard overview
class AdminDashboardView(TemplateView):
    template_name = "admin/dashboard.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['total_sales'] = Order.objects.filter(status='delivered').count()
        context['total_revenue'] = sum(o.total_price for o in Order.objects.filter(status='delivered'))
        context['total_customers'] = User.objects.count()  # Works with custom user model
        context['low_stock'] = Product.objects.filter(stock__lte=5)
        return context

# Products
class ProductListView(ListView):
    model = Product
    template_name = "admin/products_list.html"

class ProductCreateView(CreateView):
    model = Product
    fields = ['name', 'category', 'price', 'stock', 'description']
    template_name = "admin/product_form.html"
    success_url = reverse_lazy('core:products_list')  # Updated to correct app namespace

class ProductUpdateView(UpdateView):
    model = Product
    fields = ['name', 'category', 'price', 'stock', 'description']
    template_name = "admin/product_form.html"
    success_url = reverse_lazy('core:products_list')

# Orders
class OrderListView(ListView):
    model = Order
    template_name = "admin/orders_list.html"

class OrderUpdateStatusView(UpdateView):
    model = Order
    fields = ['status']
    template_name = "admin/order_update.html"
    success_url = reverse_lazy('core:orders_list')

# Coupons
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

# Customers
class CustomerListView(ListView):
    model = User  # Uses the custom User model now
    template_name = "admin/customers_list.html"


# naseem.9423!



# https://myaccount.google.com
# https://myaccount.google.com/apppasswords




# Feature Checklist for a Polished B2C Django E-Commerce Template
# 1. User Accounts & Authentication

#  Signup / login / logout with email

#  Password reset via email (already done ✅)

#  User profile page with order history

#  Address book (shipping / billing addresses)

# 2. Product Management

#  Product categories (e.g., electronics, clothing)

#  Product detail page (images, description, price, stock)

#  Product variants (size, color, etc.)

#  Search & filtering (by price, category, tags)

#  Wishlist / save for later

# 3. Shopping Cart

#  Add to cart (with quantity update)

#  Remove items from cart

#  Persistent cart (saved even after login/logout)

#  Display subtotal, shipping, tax, total

# 4. Checkout & Payments

#  Guest checkout option

#  Multiple shipping addresses

#  Stripe (already done ✅)

#  PayPal integration (optional)

#  Cash on Delivery option

# 5. Orders & Invoices

#  Order confirmation page ✅

#  Order tracking (status: pending, shipped, delivered)

#  Downloadable invoice (PDF)

#  Email notifications (order placed, shipped, delivered)




# 6. Admin & Store Management

#  Admin dashboard with sales overview

#  Manage products, categories, stock

#  Manage orders (change status, refund, cancel)

#  Discount coupons & promo codes

#  Customer management (list of customers, emails)




# 7. UX & Frontend

#  Tailwind CSS + responsive design (already using ✅)

#  Modern checkout flow with progress steps (Cart → Shipping → Payment → Confirmation)

#  Product image zoom & gallery slider

#  Featured products & categories on homepage

#  Reviews & ratings (star system)

# 8. Extra Features for More Value

#  Multi-currency support

#  Multi-language support

#  Newsletter subscription (Mailchimp/SendGrid integration)

#  SEO-friendly URLs & meta tags

#  Social login (Google, Facebook)

# 🚀 Value After This Stage

# You can sell it as a Django e-commerce template on marketplaces.

# Price range: $500 – $2,000 (one-time license or multiple sales).

# Perfect for freelancing gigs on Upwork/Fiverr (customizing for clients).



# https://developer.paypal.com/

# 501234567