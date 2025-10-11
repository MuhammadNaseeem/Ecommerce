from django.core.mail import send_mail
from django.conf import settings
from django.template.loader import render_to_string

def send_order_email(order, template_name, subject):
    if not order.user or not order.user.email:
        return  # No email to send

    context = {"order": order}
    message = render_to_string(template_name, context)
    send_mail(
        subject,
        "",
        settings.DEFAULT_FROM_EMAIL,
        [order.user.email],
        html_message=message,
        fail_silently=False,
    )


