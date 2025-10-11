from products.models import Product

def cart_summary(request):
    cart = request.session.get("cart", {})
    count = 0
    total = 0

    for pid, item in cart.items():
        try:
            product = Product.objects.get(id=pid)
            qty = int(item.get("quantity", 0))
            count += qty
            total += product.price * qty
        except Product.DoesNotExist:
            continue

    return {
        "cart_item_count": count,
        "cart_total_amount": total,
    }


