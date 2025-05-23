from django.shortcuts import get_object_or_404, redirect, render
from django.core.paginator import Paginator
from django.urls import reverse
from django.utils import timezone
from accounts.models import Profile
from products.forms import CheckoutForm
from .models import (
    Cart,
    CartItem,
    Category,
    Color,
    Order,
    OrderItem,
    Size,
    Product,
    ProductImage,
    Bd_devary,
    Cn_devary,
)
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import HttpResponseForbidden, JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST
import json


# Create your views here.
def homepage(request):
    categories = Category.objects.all()
    products_by_category = {}  # Dictionary to store products grouped by category
    for category in categories:
        products = (
            Product.objects.filter(categories=category)
            .prefetch_related("colors", "sizes")
            .order_by("-id")[:8]
        )
        if products.exists():
            products_by_category[category] = products

    context = {
        "products_by_category": products_by_category,  # Dictionary with products grouped by category
        "categories": categories,
        "colors": Color.objects.all(),
        "sizes": Size.objects.all(),
    }

    print(products_by_category)

    return render(request, "home.html", context)


def products_page(request):
    category_id = request.GET.get(
        "category", None
    )  # Get category ID from query parameters
    selected_category = None
    categories = Category.objects.all()  # Fetch all categories

    # Fetch all products with related fields optimized
    products = (
        Product.objects.all()
        .prefetch_related("images", "colors", "sizes")
        .order_by("-created_at")
    )

    if category_id:
        try:
            selected_category = Category.objects.get(id=category_id)
            products = products.filter(categories=selected_category)
        except Category.DoesNotExist:
            selected_category = None

    # PAGINATION
    paginator = Paginator(products, 12)  # Show 12 products per page
    page_number = request.GET.get(
        "page"
    )  # Get the current page number from the request
    page_obj = paginator.get_page(
        page_number
    )  # Get the products for the requested page

    context = {
        "page_obj": page_obj,  # Use `page_obj` instead of `products`
        "categories": categories,
        "selected_category": selected_category,
        "category_id": category_id,
    }

    return render(request, "products/productspage.html", context)


def product_detail(request, product_id):
    # Fetch the product and prefetch related objects (images, colors, sizes)
    product = get_object_or_404(
        Product.objects.prefetch_related("images", "colors", "sizes"), id=product_id
    )

    return render(request, "products/product_detail.html", {"product": product})


@login_required
def add_to_cart(request, product_id):
    if request.method == "POST":
        product = get_object_or_404(Product, id=product_id)
        selected_color = request.POST.get("selected_color") or None
        selected_size = request.POST.get("selected_size") or None

        if product.colors.all().exists() and not selected_color:
            messages.error(request, "Please select a color before adding to cart.")
            return redirect("product_detail", product_id=product.id)

        if product.sizes.all().exists() and not selected_size:
            messages.error(request, "Please select a size before adding to cart.")
            return redirect("product_detail", product_id=product.id)

        cart, created = Cart.objects.get_or_create(user=request.user)

        cart_item, item_created = CartItem.objects.get_or_create(
            cart=cart,
            product=product,
            color=selected_color if product.colors.all().exists() else None,
            size=selected_size if product.sizes.all().exists() else None,
        )

        if not item_created:
            cart_item.quantity += 1
            cart_item.save()

        messages.success(
            request,
            f"{product.name} ({selected_color}, {selected_size}) added to cart.",
        )
        return redirect("cart_detail")
    else:
        # Redirect to product detail page if the request is not POST
        return redirect("product_detail", product_id=product_id)


@login_required
def increse_product_quantity(request, item_id):
    product = Product.objects.get(id=item_id)

    cart, created = Cart.objects.get_or_create(user=request.user)
    cart_item, item_created = CartItem.objects.get_or_create(cart=cart, product=product)

    if not item_created:
        cart_item.quantity += 1
        cart_item.save()

    messages.success(request, f"{product.name} added to cart.")
    return redirect("cart_detail")


@login_required
def decrese_product_quantity(request, item_id):
    product = Product.objects.get(id=item_id)

    cart, created = Cart.objects.get_or_create(user=request.user)
    cart_item, item_created = CartItem.objects.get_or_create(cart=cart, product=product)

    if not item_created:
        cart_item.quantity -= 1
        cart_item.save()

    messages.success(request, f"{product.name} added to cart.")
    return redirect("cart_detail")


@login_required
def cart_detail(request):
    # Fetch all objects for Cn_devary and Bd_devary
    Cnd = Cn_devary.objects.all()
    Bdd = Bd_devary.objects.all()

    # Get or create the cart for the current user
    cart, created = Cart.objects.get_or_create(user=request.user)

    # Combine all context data into a single dictionary
    context = {
        "cart": cart,
        "Cnd": Cnd,
        "Bdd": Bdd,
    }

    # Render the template with the combined context
    return render(request, "cart/cart_detail.html", context)


@login_required
def remove_from_cart(request, item_id):
    cart_item = get_object_or_404(CartItem, id=item_id, cart__user=request.user)
    cart_item.delete()
    messages.success(request, "Item removed from cart.")
    return redirect("cart_detail")


@login_required
def checkout(request):
    cart = request.user.cart
    if not cart.items.exists():
        return redirect("cart_detail")

    try:
        profile = Profile.objects.get(user=request.user)
    except Profile.DoesNotExist:
        profile = None

    initial_data = {
        "recipient_name": profile.name if profile else request.user.username,
        "phone_number": profile.mobile_number if profile else "",
        "email": request.user.email,
        "shipping_address": profile.address if profile else "",
    }

    if request.method == "POST":
        form = CheckoutForm(request.POST)
        if form.is_valid():
            # Create order WITHOUT specifying order_ref - let the model handle it
            order = Order.objects.create(
                user=request.user,
                cart=cart,  # Add the cart relationship
                recipient_name=form.cleaned_data["recipient_name"],
                phone_number=form.cleaned_data["phone_number"],
                email=form.cleaned_data["email"],
                shipping_address=form.cleaned_data[
                    "shipping_address"
                ],  # ✅ Correct key
                city=form.cleaned_data["city"],
                postal_code=form.cleaned_data["postal_code"],
                devary_type=form.cleaned_data["devary_type"],
                order_status="pending",
            )

            # Add order items
            for item in cart.items.all():
                OrderItem.objects.create(
                    order=order,
                    product=item.product,
                    quantity=item.quantity,
                    color=item.color,
                    size=item.size,
                )

            # Clear the cart
            cart.items.all().delete()

            # Use order_ref instead of id
            # return redirect(reverse("create_payment_session", kwargs={"order_ref": order.order_ref}))
            return redirect("order_detail", order_ref=order.order_ref)

    else:
        form = CheckoutForm(initial=initial_data)

    return render(request, "cart/checkout.html", {"form": form, "cart": cart})


@login_required
def invoice(request, order_ref):
    print(order_ref)
    order = get_object_or_404(
        Order, order_ref=order_ref
    )  # Ensures 404 if order doesn't exist
    order_items = order.order_items.all()  # Fetch all order items related to this order

    return render(
        request, "cart/invoice.html", {"order": order, "order_items": order_items}
    )


def order_success(request, order_ref):
    try:
        order = (
            Order.objects.select_related("user", "cart")
            .prefetch_related("order_items")
            .get(order_ref=order_ref)
        )
    except Order.DoesNotExist:
        return render(request, "errors/404.html", status=404)

    context = {"order": order, "items": order.order_items.all()}
    return render(request, "cart/order_success.html", context)


@csrf_exempt
@require_POST
def update_cart_item(request, item_id):
    try:
        # Parse the JSON data from the request body
        data = json.loads(request.body)
        new_quantity = data.get("quantity")

        # Validate the new quantity
        if not isinstance(new_quantity, int) or new_quantity < 1:
            return JsonResponse(
                {"success": False, "error": "Invalid quantity"}, status=400
            )

        # Fetch the cart item
        cart_item = CartItem.objects.get(id=item_id, cart__user=request.user)

        # Update the quantity
        cart_item.quantity = new_quantity
        cart_item.save()

        # Return a success response
        return JsonResponse(
            {
                "success": True,
                "new_quantity": cart_item.quantity,
                "new_total_price": cart_item.total_price(),  # Assuming `total_price()` is a method in CartItem
            }
        )
    except CartItem.DoesNotExist:
        return JsonResponse(
            {"success": False, "error": "Cart item not found"}, status=404
        )
    except Exception as e:
        return JsonResponse({"success": False, "error": str(e)}, status=500)


def delete_order(request, order_ref):  # Changed from order_id to order_ref
    if request.method != "POST":
        messages.error(request, "Invalid request method.")
        return redirect("dashboard")

    order = get_object_or_404(Order, order_ref=order_ref)

    if order.user != request.user:
        return HttpResponseForbidden("You do not have permission to delete this order.")

    try:
        order.delete()
        messages.success(request, "Your order has been deleted successfully.")
    except Exception as e:
        messages.error(request, f"Failed to delete order: {str(e)}")

    return redirect("dashboard")


def About_page(request):
    return render(request, "info/about.html")


def Contact_page(request):
    return render(request, "info/contact.html")
