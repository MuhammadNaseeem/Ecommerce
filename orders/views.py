from django.shortcuts import render, redirect, get_object_or_404
from django.conf import settings
from django.urls import reverse
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import HttpResponse
from decimal import Decimal
import stripe
from xhtml2pdf import pisa
from django.template.loader import render_to_string, get_template

from cart.cart import Cart
from .models import Order, OrderItem, ShippingAddress
from .utils import send_order_email

# -------------------- PAYMENT KEYS --------------------
stripe.api_key = settings.STRIPE_SECRET_KEY

# -------------------- CHECKOUT PAGE --------------------
def checkout(request):
    cart = Cart(request)
    if not cart or len(cart) == 0:
        messages.warning(request, "Your cart is empty.")
        return redirect("cart:cart_detail")

    addresses = ShippingAddress.objects.filter(user=request.user) if request.user.is_authenticated else []

    cart_items = []
    subtotal = Decimal("0.00")
    for item in cart:
        product = item["product"]
        quantity = item["quantity"]
        line_total = product.price * quantity
        cart_items.append({"product": product, "quantity": quantity, "line_total": line_total})
        subtotal += line_total

    shipping_fee = Decimal("10.00") if subtotal > 0 else Decimal("0.00")
    tax = subtotal * Decimal("0.10")
    total_price = subtotal + shipping_fee + tax

    return render(request, "orders/checkout.html", {
        "cart_items": cart_items,
        "subtotal": subtotal,
        "shipping_fee": shipping_fee,
        "tax": tax,
        "total_price": total_price,
        "addresses": addresses,
        "STRIPE_PUBLIC_KEY": settings.STRIPE_PUBLIC_KEY
    })

# -------------------- CHECKOUT SUCCESS --------------------
@login_required
def checkout_success(request):
    order = Order.objects.filter(user=request.user).order_by("-created_at").first()
    if not order:
        messages.error(request, "No order found.")
        return redirect("cart:cart_detail")
    return render(request, "orders/checkout_success.html", {"order": order})

# -------------------- STRIPE CHECKOUT --------------------
def create_checkout_session(request):
    cart = Cart(request)
    if not cart or len(cart) == 0:
        messages.error(request, "Your cart is empty.")
        return redirect("cart:cart_detail")

    line_items = [{
        'price_data': {
            'currency': 'usd',
            'product_data': {'name': item['product'].name},
            'unit_amount': int(item['product'].price * 100),
        },
        'quantity': item['quantity'],
    } for item in cart]

    session = stripe.checkout.Session.create(
        payment_method_types=['card'],
        line_items=line_items,
        mode='payment',
        success_url=request.build_absolute_uri(reverse('orders:checkout_success')),
        cancel_url=request.build_absolute_uri(reverse('orders:checkout')),
    )

    return redirect(session.url, code=303)

# -------------------- COD CHECKOUT --------------------
@login_required
def cod_checkout(request):
    cart = Cart(request)
    if not cart or len(cart) == 0:
        messages.warning(request, "Your cart is empty.")
        return redirect("cart:cart_detail")

    shipping_address_id = request.session.get("shipping_address_id")
    shipping_address = get_object_or_404(ShippingAddress, id=shipping_address_id) if shipping_address_id else None

    subtotal = sum(item['product'].price * item['quantity'] for item in cart)
    shipping_fee = Decimal("10.00") if subtotal > 0 else Decimal("0.00")
    tax = subtotal * Decimal("0.10")
    total_price = subtotal + shipping_fee + tax

    order = Order.objects.create(
        user=request.user,
        shipping_address=shipping_address,
        subtotal=subtotal,
        shipping_fee=shipping_fee,
        tax_amount=tax,
        total_price=total_price,
        status=Order.PENDING,
        payment_method=Order.COD
    )

    for item in cart:
        OrderItem.objects.create(
            order=order,
            product=item['product'],
            quantity=item['quantity'],
            price=item['product'].price
        )

    cart.clear()
    send_order_email(order, "orders/emails/order_placed.html", "Your Order has been Placed!")
    messages.success(request, "Order placed! Please pay on delivery.")
    return redirect("orders:checkout_success")

# -------------------- ORDER CONFIRMATION --------------------
def order_confirmation(request, order_id):
    order = get_object_or_404(Order, id=order_id)
    return render(request, "orders/order_confirmation.html", {"order": order})

# -------------------- DOWNLOAD INVOICE --------------------
def generate_invoice_pdf(request, order_id):
    order = get_object_or_404(Order, id=order_id, user=request.user)
    template_path = 'orders/invoice.html'
    context = {'order': order}

    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = f'attachment; filename="invoice_{order.id}.pdf"'

    template = get_template(template_path)
    html = template.render(context)
    pisa_status = pisa.CreatePDF(html, dest=response)

    if pisa_status.err:
        return HttpResponse('Error generating PDF <pre>' + html + '</pre>')
    return response

# -------------------- ADMIN UPDATE ORDER STATUS --------------------
from django.contrib.admin.views.decorators import staff_member_required

@staff_member_required
def update_order_status(request, order_id, status):
    order = get_object_or_404(Order, id=order_id)
    if status in [Order.PENDING, Order.SHIPPED, Order.COMPLETED, Order.CANCELED]:
        order.status = status
        order.save()
    return redirect("admin:orders_order_change", order.id)

# Optional: orders home redirect
def orders_home(request):
    return redirect('orders:checkout')


