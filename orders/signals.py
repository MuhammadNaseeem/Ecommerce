# signals.py
from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import Order
from .utils import send_order_email

@receiver(post_save, sender=Order)
def handle_order_status(sender, instance, created, **kwargs):
    """
    - Calculate totals when order is created
    - Send email notifications when status changes
    """
    if created:
        instance.calculate_totals()
        if instance.user and instance.payment_method != Order.COD:
            send_order_email(instance, "orders/emails/order_placed.html", "Your Order has been Placed!")
    else:
        # Send email when status changes
        if instance.status == Order.SHIPPED:
            send_order_email(instance, "orders/emails/order_shipped.html", "Your Order has been Shipped!")
        elif instance.status == Order.COMPLETED:
            send_order_email(instance, "orders/emails/order_delivered.html", "Your Order has been Delivered!")


