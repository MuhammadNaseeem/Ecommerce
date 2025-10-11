# cart/cart.py
from decimal import Decimal
from products.models import Product

class Cart:
    def __init__(self, request):
        """
        Initialize the cart from the session.
        """
        self.session = request.session
        cart = self.session.get("cart")
        if not cart:
            cart = self.session["cart"] = {}
        self.cart = cart

    def add(self, product, quantity=1, override_quantity=False):
        """
        Add a product to the cart or update its quantity.
        Price is stored as string for JSON serialization.
        """
        product_id = str(product.id)
        if product_id not in self.cart:
            self.cart[product_id] = {"quantity": 0, "price": str(product.price)}

        if override_quantity:
            self.cart[product_id]["quantity"] = quantity
        else:
            self.cart[product_id]["quantity"] += quantity

        self.save()

    def remove(self, product):
        """
        Remove a product from the cart.
        """
        product_id = str(product.id)
        if product_id in self.cart:
            del self.cart[product_id]
            self.save()

    def clear(self):
        """
        Remove all items from the cart.
        """
        self.session["cart"] = {}
        self.save()

    def save(self):
        """
        Mark the session as modified.
        """
        self.session.modified = True

    def __iter__(self):
        """
        Iterate over items in the cart and attach Product instances.
        Convert price from string to Decimal for calculations, but do not save Decimal in session.
        """
        product_ids = self.cart.keys()
        products = Product.objects.filter(id__in=product_ids)
        cart_copy = self.cart.copy()  # avoid modifying session

        for product in products:
            product_id = str(product.id)
            item = cart_copy[product_id]
            item["product"] = product
            item["price"] = Decimal(item["price"])
            item["total_price"] = item["price"] * item["quantity"]
            yield item

    def __len__(self):
        """
        Count total quantity of all items in the cart.
        """
        return sum(item["quantity"] for item in self.cart.values())

    def subtotal(self):
        """
        Total price of all items before tax and shipping.
        """
        return sum(item["total_price"] for item in self.__iter__())

    def shipping(self):
        """
        Flat shipping fee; return 0 if cart is empty.
        """
        return Decimal("10.00") if len(self) > 0 else Decimal("0.00")

    def tax(self, tax_rate=0.1):
        """
        Calculate tax (default 10%).
        """
        return self.subtotal() * Decimal(tax_rate)

    def total(self):
        """
        Total including subtotal + shipping + tax.
        """
        return self.subtotal() + self.shipping() + self.tax()

    def as_dict(self):
        """
        Return cart totals as JSON-serializable dict (for AJAX).
        """
        return {
            "subtotal": float(self.subtotal()),
            "shipping": float(self.shipping()),
            "tax": float(self.tax()),
            "total": float(self.total()),
            "count": self.__len__(),
        }


