from django.db import models
from django.conf import settings
from products.models import Product

# -------------------- SHIPPING ADDRESS MODEL --------------------
class ShippingAddress(models.Model):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, 
        on_delete=models.CASCADE, 
        related_name="shipping_addresses",
        blank=True, null=True  # allow guest users
    )
    full_name = models.CharField(max_length=255)
    email = models.EmailField(blank=True, null=True)
    address_line = models.CharField(max_length=255)
    city = models.CharField(max_length=100)
    postal_code = models.CharField(max_length=20)
    country = models.CharField(max_length=100)
    is_default = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.full_name}, {self.address_line}, {self.city}"

# -------------------- ORDER MODEL --------------------
class Order(models.Model):
    # Order status
    PENDING = "Pending"
    PAID = "Paid"
    SHIPPED = "Shipped"
    COMPLETED = "Completed"
    CANCELED = "Canceled"

    STATUS_CHOICES = [
        (PENDING, "Pending"),
        (PAID, "Paid"),
        (SHIPPED, "Shipped"),
        (COMPLETED, "Completed"),
        (CANCELED, "Canceled"),
    ]

    # Payment method
    STRIPE = "Stripe"
    PAYPAL = "PayPal"
    COD = "Cash on Delivery"
    PAYMENT_CHOICES = [
        (STRIPE, "Stripe"),
        (PAYPAL, "PayPal"),
        (COD, "Cash on Delivery"),
    ]

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="orders",
        blank=True, null=True  # allow guest checkout
    )
    shipping_address = models.ForeignKey(
        ShippingAddress,
        on_delete=models.SET_NULL,
        null=True,
        related_name="orders"
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    # Pricing
    subtotal = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    shipping_fee = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    tax_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    total_price = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default=PENDING)
    payment_method = models.CharField(max_length=20, choices=PAYMENT_CHOICES, default=STRIPE)

    # Payment tracking
    stripe_payment_intent = models.CharField(max_length=255, blank=True, null=True)
    paypal_transaction_id = models.CharField(max_length=255, blank=True, null=True)
    cod_confirmed = models.BooleanField(default=False)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return f"Order #{self.pk} - {self.status}"

    def is_paid(self):
        return self.status == self.PAID

    def calculate_totals(self):
        """
        Update subtotal, tax, shipping_fee, and total_price automatically.
        """
        subtotal = sum(item.subtotal() for item in self.items.all())
        shipping_fee = 10.00 if subtotal > 0 else 0.00
        tax_amount = subtotal * 0.1  # 10% tax
        total_price = subtotal + shipping_fee + tax_amount

        self.subtotal = subtotal
        self.shipping_fee = shipping_fee
        self.tax_amount = tax_amount
        self.total_price = total_price
        self.save()

# -------------------- ORDER ITEM MODEL --------------------
class OrderItem(models.Model):
    order = models.ForeignKey(Order, related_name="items", on_delete=models.CASCADE)
    product = models.ForeignKey(Product, on_delete=models.SET_NULL, null=True)
    quantity = models.PositiveIntegerField(default=1)
    price = models.DecimalField(max_digits=10, decimal_places=2)

    def subtotal(self):
        return self.price * self.quantity

    def __str__(self):
        return f"{self.product} × {self.quantity}"





