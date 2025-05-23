from django.db.models.signals import post_save, pre_save
from django.dispatch import receiver
from decimal import Decimal, ROUND_HALF_UP
import math
from django.db.models.signals import m2m_changed
from .models import (
    Category,
    Currency,
    MonthlyTotalProfit,
    Order,
    Payment,
    Product,
    ProfitMargin,
)


@receiver(post_save, sender=Category)
def update_product_prices(sender, instance, **kwargs):
    """Update product prices when the category is updated."""
    for product in instance.products.all():
        product.save()  # This will trigger the `save` method in Product and recalculate the price.


# ✅ This signal will automatically update the prices of all products in a category when the category is updated.
# This is useful when the delivery cost or counting choice of a category changes, and you want to update the prices of all products in that category.


@receiver(post_save, sender=Currency)
def update_product_prices_on_currency_change(sender, instance, **kwargs):
    """Update product prices when the currency rate is updated."""
    for product in Product.objects.all():
        product.save()  # Trigger save() to recalculate the price based on the new currency rate.


@receiver(pre_save, sender=Order)
def update_total_amount(sender, instance, **kwargs):
    # Ensure total_amount is recalculated before saving the Order
    instance.total_amount = sum(
        item.total_price() for item in instance.order_items.all()
    )


@receiver(post_save, sender=Payment)
def update_profit_on_successful_payment(sender, instance, **kwargs):
    """Run profit margin update only after a successful payment."""
    if instance.payment_status == "valid":
        ProfitMargin.update_profit_margin()


@receiver(post_save, sender=Payment)
def update_profit_on_successful_payment(sender, instance, **kwargs):
    """Run profit margin update only after a successful payment."""
    if instance.payment_status == "valid":
        MonthlyTotalProfit.update_monthly_total_profit()


@receiver(m2m_changed, sender=Product.categories.through)
def update_product_price(sender, instance, action, **kwargs):
    if action == "post_add":  # Trigger only after categories are added
        instance.calculate_price()
        instance.save()
