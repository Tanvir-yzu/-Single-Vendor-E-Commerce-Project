# payments/signals.py

from django.dispatch import Signal
from django.core.mail import send_mail
from django.conf import settings

payment_success_signal = Signal()

def send_payment_emails(sender, order, **kwargs):
    """Handle payment confirmation emails to user and admin"""
    try:
        user_email = order.user.email
        admin_email = settings.DEFAULT_FROM_EMAIL
        
        if not user_email:
            raise ValueError("User email missing in order")
            
        if not admin_email:
            raise ValueError("Admin email not configured in settings")

        # User notification
        send_mail(
            subject="Payment Successful",
            message=f"Hello {order.user.username},\n\nYour payment was successful. Thank you for your purchase!",
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[user_email],
            fail_silently=False
        )

        # Admin notification
        send_mail(
            subject="New Payment Received",
            message=f"A new payment was received from {order.user.username} ({user_email}).",
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[admin_email],
            fail_silently=False
        )

    except Exception as e:
        print(f"Email sending failed: {str(e)}")
        raise

payment_success_signal.connect(send_payment_emails)