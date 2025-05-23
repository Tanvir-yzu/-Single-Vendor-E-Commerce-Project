from products.models import Currency, CartItem


def currency_rate(request):
    try:
        rate = Currency.objects.latest("id")  # Fetch latest rate all contections
    except Currency.DoesNotExist:
        rate = None
    return {"currency_rate": rate}


def cart_count(request):
    total_items = 0

    if request.user.is_authenticated:  # Ensure user is logged in
        total_items = CartItem.objects.filter(cart__user=request.user).count()

    return {"cart_items": total_items}
