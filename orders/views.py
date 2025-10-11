from django.shortcuts import render, redirect, get_object_or_404
from django.conf import settings
from django.urls import reverse
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import HttpResponse
from decimal import Decimal
import stripe
# import paypalrestsdk
from xhtml2pdf import pisa
from django.template.loader import render_to_string, get_template

from cart.cart import Cart
from .models import Order, OrderItem, ShippingAddress
from .utils import send_order_email

from django.core.mail import EmailMultiAlternatives
from django.template.loader import render_to_string
from django.conf import settings


# -------------------- PAYMENT KEYS --------------------
import stripe

# Stripe configuration
stripe.api_key = settings.STRIPE_SECRET_KEY

# ✅ PayPal removed, no need to configure anything for PayPal

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
    """
    This view is used for displaying order confirmation after
    payment via Stripe, PayPal, or COD.
    """
    # Get the latest order for the user
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


# -------------------- PAYPAL CHECKOUT --------------------
@login_required
def create_paypal_payment(request):
    cart = Cart(request)
    if not cart or len(cart) == 0:
        messages.error(request, "Your cart is empty.")
        return redirect("cart:cart_detail")

    subtotal = sum(item['product'].price * item['quantity'] for item in cart)
    shipping_fee = Decimal("10.00") if subtotal > 0 else Decimal("0.00")
    tax = subtotal * Decimal("0.10")
    total_price = subtotal + shipping_fee + tax

    items = [{
        "name": item['product'].name,
        "sku": str(item['product'].id),
        "price": str(item['product'].price),
        "currency": "USD",
        "quantity": item['quantity']
    } for item in cart]

    payment = paypalrestsdk.Payment({
        "intent": "sale",
        "payer": {"payment_method": "paypal"},
        "redirect_urls": {
            "return_url": request.build_absolute_uri(reverse("orders:paypal_success")),
            "cancel_url": request.build_absolute_uri(reverse("orders:checkout")),
        },
        "transactions": [{
            "item_list": {"items": items},
            "amount": {"total": str(total_price), "currency": "USD"},
            "description": "Purchase from MyStore"
        }]
    })

    if payment.create():
        for link in payment.links:
            if link.method == "REDIRECT":
                return redirect(link.href)
    messages.error(request, "Error creating PayPal payment.")
    return redirect("orders:checkout")


@login_required
def paypal_success(request):
    payer_id = request.GET.get('PayerID')
    payment_id = request.GET.get('paymentId')
    payment = paypalrestsdk.Payment.find(payment_id)

    if payment.execute({"payer_id": payer_id}):
        cart = Cart(request)
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
            status=Order.PAID,
            payment_method=Order.PAYPAL,
            paypal_transaction_id=payment.id
        )

        for item in cart:
            OrderItem.objects.create(
                order=order,
                product=item['product'],
                quantity=item['quantity'],
                price=item['product'].price
            )

        cart.clear()
        # Send email
        send_order_email(order, "orders/emails/order_placed.html", "Your Order has been Placed!")
        messages.success(request, "Payment successful via PayPal!")
        return redirect("orders:checkout_success")
    messages.error(request, "PayPal payment failed.")
    return redirect("orders:checkout")


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
def download_invoice(request, order_id):
    order = get_object_or_404(Order, id=order_id)
    html = render_to_string("orders/invoice.html", {"order": order})
    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = f'attachment; filename="invoice_{order.id}.pdf"'
    pisa.CreatePDF(html, dest=response)
    return response

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



# from django.shortcuts import render, redirect
# from django.urls import reverse
# from decimal import Decimal
# from paypalcheckoutsdk.orders import OrdersCreateRequest, OrdersCaptureRequest
# from paypalcheckoutsdk.core import PayPalHttpClient, SandboxEnvironment

# # PayPal sandbox credentials
# CLIENT_ID = "YOUR_PAYPAL_CLIENT_ID"
# CLIENT_SECRET = "YOUR_PAYPAL_CLIENT_SECRET"

# environment = SandboxEnvironment(client_id=CLIENT_ID, client_secret=CLIENT_SECRET)
# paypal_client = PayPalHttpClient(environment)


# def create_paypal_payment(request):
#     # Calculate total amount dynamically from the user's cart
#     cart = request.session.get("cart", {})  # Assuming cart stored in session
#     total_amount = sum(Decimal(item['price']) * item['quantity'] for item in cart.values())
    
#     if total_amount <= 0:
#         return redirect('orders:checkout')

#     request_order = OrdersCreateRequest()
#     request_order.prefer("return=representation")
#     request_order.request_body(
#         {
#             "intent": "CAPTURE",
#             "purchase_units": [
#                 {
#                     "amount": {
#                         "currency_code": "USD",
#                         "value": str(total_amount)
#                     }
#                 }
#             ],
#             "application_context": {
#                 "return_url": request.build_absolute_uri(reverse('orders:paypal_success')),
#                 "cancel_url": request.build_absolute_uri(reverse('orders:checkout'))
#             }
#         }
#     )

#     try:
#         response = paypal_client.execute(request_order)
#         for link in response.result.links:
#             if link.rel == "approve":
#                 return redirect(link.href)
#     except Exception as e:
#         return render(request, "orders/paypal_error.html", {"error": str(e)})


# def paypal_success(request):
#     token = request.GET.get("token")  # PayPal returns token
#     if token:
#         # Capture the payment
#         request_capture = OrdersCaptureRequest(token)
#         request_capture.request_body({})
#         try:
#             capture_response = paypal_client.execute(request_capture)
#             # Optional: Save order to DB here
#             return render(request, "orders/paypal_success.html", {"capture": capture_response.result})
#         except Exception as e:
#             return render(request, "orders/paypal_error.html", {"error": str(e)})
#     return redirect('orders:checkout')


# def orders_home(request):
#     # For example, show a list of user’s orders or redirect to checkout
#     return redirect('orders:checkout')


