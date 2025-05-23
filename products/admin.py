from django.contrib import admin
from django.contrib.admin import TabularInline
from .models import (
    Cart,
    CartItem,
    Category,
    Color,
    MonthlyTotalProfit,
    Order,
    OrderItem,
    Payment,
    ProfitMargin,
    Size,
    Product,
    ProductImage,
    Currency,
    Cn_devary,
    Bd_devary,
)
from django.core.mail import send_mail
from django.template.loader import render_to_string
from django.conf import settings


class ProductImageInline(TabularInline):
    model = ProductImage
    extra = 1


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ("name", "created_at", "updated_at")
    search_fields = ("name",)
    ordering = ("name",)


@admin.register(Color)
class ColorAdmin(admin.ModelAdmin):
    list_display = ("name", "created_at", "updated_at")
    search_fields = ("name",)
    ordering = ("name",)


@admin.register(Size)
class SizeAdmin(admin.ModelAdmin):
    list_display = ("name", "created_at", "updated_at")
    search_fields = ("name",)
    ordering = ("name",)


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = (
        "name",
        "get_categories",
        "price",
        "original_price",
        "profit_margin",
        "available",
        "created_at",
        "weight",
        "dimensions",
        "brand",
        "description",
    )
    list_filter = ("categories", "available", "colors", "sizes")
    search_fields = ("name", "categories__name", "brand")
    ordering = ("name",)
    filter_horizontal = ("categories", "colors", "sizes")
    list_editable = ("original_price", "profit_margin", "available")
    readonly_fields = ("created_at", "updated_at", "price")
    inlines = [ProductImageInline]

    fieldsets = (
        ("Basic Info", {"fields": ("name", "categories")}),
        (
            "Stock & Pricing",
            {
                "fields": (
                    "original_price",
                    "profit_margin",
                    "price",
                    "available",
                    "weight",
                )
            },
        ),
        (
            "Attributes",
            {"fields": ("colors", "sizes", "brand", "dimensions", "description")},
        ),
        ("Timestamps", {"fields": ("created_at", "updated_at")}),
    )

    def get_categories(self, obj):
        return ", ".join([category.name for category in obj.categories.all()])

    get_categories.short_description = "Categories"


@admin.register(Currency)
class CurrencyAdmin(admin.ModelAdmin):
    list_display = ("rate",)
    search_fields = ("rate",)
    list_filter = ("rate",)


@admin.register(Cn_devary)
class Cn_devaryAdmin(admin.ModelAdmin):
    list_display = (
        "devary_type",
        "devary_cost",
        "devary_time",
        "created_at",
        "updated_at",
    )
    list_filter = ("devary_cost", "created_at", "updated_at")
    search_fields = ("devary_type", "devary_time")
    readonly_fields = ("created_at", "updated_at")
    list_editable = ("devary_cost",)
    ordering = ("devary_type",)

    fieldsets = (
        ("Basic Information", {"fields": ("devary_type", "devary_cost")}),
        ("Time Information", {"fields": ("devary_time",)}),
        (
            "Timestamps",
            {"fields": ("created_at", "updated_at"), "classes": ("collapse",)},
        ),
    )

    def get_queryset(self, request):
        return super().get_queryset(request).select_related()


@admin.register(Bd_devary)
class Bd_devaryAdmin(admin.ModelAdmin):
    list_display = (
        "devary_type",
        "devary_cost",
        "devary_time",
        "created_at",
        "updated_at",
    )
    list_filter = ("devary_cost", "created_at", "updated_at")
    search_fields = ("devary_type", "devary_time")
    readonly_fields = ("created_at", "updated_at")
    list_editable = ("devary_cost",)
    ordering = ("devary_type",)

    fieldsets = (
        ("Basic Information", {"fields": ("devary_type", "devary_cost")}),
        ("Time Information", {"fields": ("devary_time",)}),
        (
            "Timestamps",
            {"fields": ("created_at", "updated_at"), "classes": ("collapse",)},
        ),
    )

    def get_queryset(self, request):
        return super().get_queryset(request).select_related()


@admin.register(Cart)
class CartAdmin(admin.ModelAdmin):
    list_display = ("user", "shipping_method", "total_cart_price")
    search_fields = ("user__username",)
    list_filter = ("shipping_method",)

    def total_cart_price(self, obj):
        return obj.total_price()

    total_cart_price.short_description = "Total Price"


@admin.register(CartItem)
class CartItemAdmin(admin.ModelAdmin):
    list_display = ("cart", "product", "quantity", "color", "size", "item_total_price")
    search_fields = ("cart__user__username", "product__name")
    list_filter = ("product",)

    def item_total_price(self, obj):
        return obj.total_price()

    item_total_price.short_description = "Total Price"


class OrderItemInline(admin.TabularInline):
    model = OrderItem
    extra = 0
    readonly_fields = ("total_price",)
    fields = ("product", "quantity", "color", "size", "total_price")

    def has_add_permission(self, request, obj):
        return False

    def has_delete_permission(self, request, obj=None):
        return False


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = (
        "order_ref",
        "user",
        "recipient_name",
        "order_status",
        "order_date",
        "total_amount",
    )
    search_fields = ("order_ref", "user__username", "recipient_name", "email")
    list_filter = ("order_status", "payment_status", "order_date")
    readonly_fields = (
        "order_ref",
        "transaction_id",
        "total_amount",
        "order_date",
        "user",
        "payment_status",
    )
    ordering = ("-order_date",)
    inlines = [OrderItemInline]

    def save_model(self, request, obj, form, change):
        if change:
            old_obj = Order.objects.get(pk=obj.pk)
            old_status = old_obj.order_status
        else:
            old_status = None

        obj.total_amount = sum(item.total_price() for item in obj.order_items.all())
        super().save_model(request, obj, form, change)

        if change and old_status != obj.order_status:
            self.send_status_update_email(request, obj)

    def save_related(self, request, form, formsets, change):
        super().save_related(request, form, formsets, change)

        obj = form.instance
        obj.total_amount = sum(item.total_price() for item in obj.order_items.all())
        obj.save()

        old_obj = Order.objects.get(pk=obj.pk)
        if old_obj.order_status != form.initial.get("order_status"):
            self.send_status_update_email(request, obj)

        # Only send email if this is a change (not a new order) and if status changed
        if change and "order_status" in form.initial:
            old_status = form.initial.get("order_status")
            if old_status != obj.order_status:
                self.send_status_update_email(request, obj)

    def send_status_update_email(self, request, order):
        subject = f"Order Status Update - {order.order_ref}"
        context = {
            "order": order,
        }

        html_message = render_to_string("emails/order_status_update.html", context)
        plain_message = render_to_string("emails/order_status_update.txt", context)

        try:
            send_mail(
                subject=subject,
                message=plain_message,
                from_email=settings.DEFAULT_FROM_EMAIL,
                recipient_list=[order.email],
                html_message=html_message,
                fail_silently=False,
            )
        except Exception as e:
            self.message_user(
                request,
                f"Failed to send email for order {order.order_ref}: {str(e)}",
                level="error",
            )


@admin.register(Payment)
class PaymentAdmin(admin.ModelAdmin):
    list_display = (
        "order",
        "transaction_id",
        "amount",
        "currency",
        "payment_status",
        "transaction_date",
    )
    list_filter = ("payment_status", "transaction_date")
    search_fields = ("transaction_id", "order__order_ref")
    readonly_fields = (
        "order",
        "transaction_id",
        "amount",
        "currency",
        "payment_status",
        "transaction_date",
    )

    def has_add_permission(self, request):
        return False

    def has_change_permission(self, request, obj=None):
        return False

    def has_delete_permission(self, request, obj=None):
        return False


@admin.register(OrderItem)
class OrderItemAdmin(admin.ModelAdmin):
    list_display = ("order", "product", "quantity", "color", "size", "total_price")
    search_fields = ("order__order_ref", "product__name")
    list_filter = ("order", "product")
    readonly_fields = ("total_price",)


@admin.register(ProfitMargin)
class ProfitMarginAdmin(admin.ModelAdmin):
    list_display = ("product", "month", "year", "total_quantity_sold", "total_profit")
    list_filter = ("year", "month", "product")
    ordering = ("-year", "-month")


@admin.register(MonthlyTotalProfit)
class MonthlyTotalProfitAdmin(admin.ModelAdmin):
    list_display = ("month", "year", "total_profit")
    list_filter = ("year", "month")
    search_fields = ("year", "month")
    ordering = ["-year", "-month"]
