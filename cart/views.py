# cart/views.py
from django.shortcuts import render, redirect, get_object_or_404
from django.views.decorators.http import require_POST
from products.models import Product
from .cart import Cart  # session-based Cart class


def cart_detail(request):
    """
    Display cart items, subtotal, shipping, tax, and total.
    """
    cart = Cart(request)
    return render(request, "cart/cart_detail.html", {
        "cart_items": list(cart),  # cart.__iter__()
        "subtotal": cart.subtotal(),
        "shipping": cart.shipping(),
        "tax": cart.tax(),
        "total": cart.total(),
    })


@require_POST
def cart_add(request, product_id):
    """
    Add a product to the cart or increase quantity.
    """
    cart = Cart(request)
    product = get_object_or_404(Product, id=product_id)
    try:
        quantity = int(request.POST.get("quantity", 1))
        if quantity < 1:
            quantity = 1
    except ValueError:
        quantity = 1

    cart.add(product=product, quantity=quantity)
    return redirect("cart:cart_detail")


@require_POST
def cart_update(request, product_id):
    """
    Update product quantity in the cart (override quantity).
    """
    cart = Cart(request)
    product = get_object_or_404(Product, id=product_id)
    try:
        quantity = int(request.POST.get("quantity", 1))
    except ValueError:
        quantity = 1

    if quantity > 0:
        cart.add(product=product, quantity=quantity, override_quantity=True)
    else:
        cart.remove(product)

    return redirect("cart:cart_detail")


@require_POST
def cart_remove(request, product_id):
    """
    Remove product from the cart.
    """
    cart = Cart(request)
    product = get_object_or_404(Product, id=product_id)
    cart.remove(product)
    return redirect("cart:cart_detail")


