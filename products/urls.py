from django.urls import path

from products.views import (
    add_to_cart,
    cart_detail,
    checkout,
    decrese_product_quantity,
    homepage,
    increse_product_quantity,
    invoice,
    order_success,
    products_page,
    product_detail,
    remove_from_cart,
    About_page,
    Contact_page,
    update_cart_item,
)

urlpatterns = [
    path("", homepage, name="home_page"),
    path("products/", products_page, name="products_page"),
    path("product/<int:product_id>/", product_detail, name="product_detail"),
    path("cart/", cart_detail, name="cart_detail"),
    path("cart/add/<int:product_id>/", add_to_cart, name="add_to_cart"),
    path("cart/remove/<int:item_id>/", remove_from_cart, name="remove_from_cart"),
    path(
        "cart/increse/<int:item_id>/",
        increse_product_quantity,
        name="increse_product_quantity",
    ),
    path(
        "cart/decrese/<int:item_id>/",
        decrese_product_quantity,
        name="decrese_product_quantity",
    ),
    path("update-cart-item/<int:item_id>/", update_cart_item, name="update_cart_item"),
    path("checkout/", checkout, name="checkout"),
    path("checkout/invoice/<str:order_ref>/", invoice, name="order_detail"),
    path(
        "order-success/<str:order_ref>/", order_success, name="order_success"
    ),  # Order success page
    path("about/", About_page, name="about_page"),
    path("contact/", Contact_page, name="contact_page"),
]
