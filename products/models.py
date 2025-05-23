from decimal import Decimal, ROUND_HALF_UP
import math
from django.db import models
from django.conf import settings
from django.utils import timezone
from django.utils.timezone import now
from django.db.models import Sum, F, ExpressionWrapper, DecimalField


class BaseModel(models.Model):
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True


# this is the model for currency
class Currency(BaseModel):
    rate = models.DecimalField(
        max_digits=10, decimal_places=2, unique=True, db_index=True
    )

    def __str__(self):
        return f"1 CNY ≈ {self.rate} BDT"


# this is the model for category
COUNTING_CHOICES = [
    ("per_kg", "The delivery cost is per kg"),
    ("per_unit", "The delivery cost is per unit"),
    ("free", "Free delivery"),
]


class Category(BaseModel):
    name = models.CharField(max_length=100, unique=True, db_index=True)
    delivery_cost = models.DecimalField(max_digits=10, decimal_places=2, default=0.0)
    counting_choice = models.CharField(
        max_length=20, choices=COUNTING_CHOICES, default="free"
    )

    def __str__(self):
        return self.name


# this is the model for color
class Color(BaseModel):
    name = models.CharField(max_length=50, unique=True, db_index=True)
    hex_code = models.CharField(max_length=7, default="#FFFFFF")

    def __str__(self):
        return self.name


# this is the model for size
class Size(BaseModel):
    name = models.CharField(max_length=50, unique=True, db_index=True)

    def __str__(self):
        return self.name


class Cn_devary(BaseModel):
    devary_type = models.CharField(
        max_length=250,
        unique=True,
        db_index=True,
        help_text="The type of devary (must be unique).",
    )
    devary_cost = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=0.0,
        help_text="The cost associated with the devary.",
    )
    devary_time = models.CharField(
        max_length=250,
        help_text="The date and time associated with the devary (optional).",
    )

    def __str__(self):
        return self.devary_type

    class Meta:
        verbose_name = "CN_Devary"
        verbose_name_plural = "CN_Devaries"


class Bd_devary(BaseModel):
    devary_type = models.CharField(
        max_length=250,
        unique=True,
        db_index=True,
        help_text="The type of devary (must be unique).",
    )
    devary_cost = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=0.0,
        help_text="The cost associated with the devary.",
    )
    devary_time = models.CharField(
        max_length=250,
        help_text="The date and time associated with the devary (optional).",
    )

    def __str__(self):
        return self.devary_type

    class Meta:
        verbose_name = "BD_Devary"


# this is the model for product
class Product(BaseModel):
    name = models.CharField(max_length=255, db_index=True)
    categories = models.ManyToManyField(Category, related_name="products")
    original_price = models.DecimalField(max_digits=10, decimal_places=2, default=0.0)
    profit_margin = models.DecimalField(max_digits=10, decimal_places=2, default=0.0)
    price = models.DecimalField(max_digits=10, decimal_places=0, default=0)
    available = models.BooleanField(default=True, db_index=True)
    colors = models.ManyToManyField(Color, related_name="products", blank=True)
    sizes = models.ManyToManyField(Size, related_name="products", blank=True)
    weight = models.DecimalField(max_digits=10, decimal_places=2, default=0.0)
    brand = models.CharField(max_length=100, blank=True, null=True, default="Unknown")
    dimensions = models.CharField(max_length=100, blank=True, null=True)
    description = models.TextField(blank=True, null=True)

    class Meta:
        indexes = [
            models.Index(fields=["name"]),
            models.Index(fields=["price"]),
            models.Index(fields=["available"]),
        ]

    def save(self, *args, **kwargs):
        # Initial save to create the instance in the database
        if not self.pk:
            super().save(*args, **kwargs)

        # Calculate delivery cost and price only if the instance already exists
        else:
            if self.categories.exists():
                self.calculate_price()
            # self.calculate_price()

        # Final save to commit changes
        super().save(*args, **kwargs)

    def calculate_price(self):
        if not self.categories.exists():
            print(
                f"Warning: No categories found for product {self.name}. Skipping price calculation."
            )
            return
        """Calculate the product price based on delivery cost, currency rate, and profit margin."""
        delivery_cost = 0
        category = self.categories.first()

        if category:
            if category.counting_choice == "per_kg":
                delivery_cost = (self.weight / 1000) * category.delivery_cost
            elif category.counting_choice == "per_unit":
                delivery_cost = category.delivery_cost
            elif category.counting_choice == "free":
                delivery_cost = 0

        print(f"Delivery cost for {self.name}: {delivery_cost}")

        try:
            currency_rate = Currency.objects.latest("created_at").rate
        except Currency.DoesNotExist:
            currency_rate = Decimal(1)

        converted_price = self.original_price * currency_rate
        self.price = math.ceil(converted_price + self.profit_margin + delivery_cost)

    @staticmethod
    def update_delivery_cost():
        for product in Product.objects.all():
            product.calculate_price()
            product.save()


# this is the model for product image
class ProductImage(BaseModel):
    product = models.ForeignKey(
        Product, on_delete=models.CASCADE, related_name="images"
    )
    image = models.ImageField(upload_to="product_images/")

    def __str__(self):
        return f"Image for {self.product.name}"


SHIPPING_CHOICES = [
    ("standard", "Standard Shipping (5-7 days)"),
    ("express", "Express Shipping (2-3 days)"),
    ("overnight", "Overnight Shipping (1 day)"),
]


class Cart(BaseModel):
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    shipping_method = models.CharField(
        max_length=20, choices=SHIPPING_CHOICES, default="standard"
    )

    def total_price(self):
        return math.ceil(sum(item.total_price() for item in self.items.all()))

    def __str__(self):
        return f"Cart of {self.user.username}"


class CartItem(BaseModel):
    cart = models.ForeignKey(Cart, related_name="items", on_delete=models.CASCADE)
    product = models.ForeignKey("Product", on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField(default=1)
    color = models.CharField(max_length=50, blank=True, null=True)
    size = models.CharField(max_length=20, blank=True, null=True)

    def total_price(self):
        price = int(self.product.price)
        total_price = price * self.quantity
        return total_price

    def __str__(self):
        return (
            f"{self.quantity} x {self.product.name} in {self.cart.user.username}'s cart"
        )


STATUS_CHOICES = [
    ("pending", "Pending"),
    ("processing", "Processing"),
    ("confirmed", "Confirmed"),
    ("packed", "Packed"),
    ("logistics", "In Logistics"),
    ("waiting", "Waiting for Delivery"),
    ("shipped", "Shipped"),
    ("delivered", "Delivered"),
    ("cancelled", "Cancelled"),
    ("completed", "Completed"),
]

SHIPPING_CHOICES2 = [
    ("self_pickup", "Self Pickup { Collect from the office }"),
    ("home_delivary", "Home Delivary"),
]


class Order(BaseModel):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    cart = models.ForeignKey("Cart", on_delete=models.CASCADE)
    order_ref = models.CharField(max_length=20, unique=True, primary_key=True)

    # Add payment fields
    transaction_id = models.CharField(max_length=100, blank=True, null=True)
    payment_status = models.CharField(
        max_length=20,
        choices=[("pending", "Pending"), ("paid", "Paid"), ("failed", "Failed")],
        default="pending",
    )
    payment_method = models.CharField(max_length=50, blank=True, null=True)

    recipient_name = models.CharField(max_length=255)
    phone_number = models.CharField(max_length=20)
    email = models.EmailField()
    city = models.CharField(max_length=100)
    postal_code = models.CharField(max_length=20)
    shipping_address = models.TextField()
    devary_type = models.CharField(
        max_length=20, choices=SHIPPING_CHOICES2, default="self_pickup"
    )
    order_status = models.CharField(
        max_length=20, choices=STATUS_CHOICES, default="pending"
    )
    order_date = models.DateTimeField(default=timezone.now)
    total_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0.0)

    def save(self, *args, **kwargs):
        if not self.order_ref:
            now = timezone.now()
            order_number = Order.objects.filter(order_date__year=now.year).count() + 1
            self.order_ref = f"{now.year % 100:02d}{now.month:02d}{now.day:02d}{self.user.username}{order_number:02d}"
        # Recalculate total_amount based on related OrderItems
        self.total_amount = sum(item.total_price() for item in self.order_items.all())
        super().save(*args, **kwargs)

    def __str__(self):
        return f"Order {self.order_ref} by {self.user.username}"


class OrderItem(BaseModel):
    order = models.ForeignKey(
        Order, related_name="order_items", on_delete=models.CASCADE
    )
    product = models.ForeignKey("Product", on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField()
    color = models.CharField(max_length=50, blank=True, null=True)
    size = models.CharField(max_length=20, blank=True, null=True)

    def total_price(self):
        # Return Decimal without converting to int to preserve cents
        return self.quantity * self.product.price

    def save(self, *args, **kwargs):
        # Save the OrderItem first
        super().save(*args, **kwargs)
        # Update the total amount of the related order
        if self.order:
            self.order.total_amount = sum(
                item.total_price() for item in self.order.order_items.all()
            )
            self.order.save()

    def __str__(self):
        return f"{self.quantity} x {self.product.name} in Order {self.order.order_ref}"


class Payment(models.Model):
    order = models.OneToOneField(
        Order, related_name="payment", on_delete=models.CASCADE
    )
    transaction_id = models.CharField(max_length=100, unique=True)
    validation_id = models.CharField(max_length=100, blank=True, null=True)
    bank_transaction_id = models.CharField(max_length=100, blank=True, null=True)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    currency = models.CharField(max_length=10)
    card_type = models.CharField(max_length=50)
    card_brand = models.CharField(max_length=50, blank=True, null=True)
    card_issuer = models.CharField(max_length=100, blank=True, null=True)
    card_issuer_country = models.CharField(max_length=50, blank=True, null=True)
    payment_status = models.CharField(
        max_length=20,
        choices=[("valid", "Valid"), ("failed", "Failed")],
        default="valid",
    )
    transaction_date = models.DateTimeField()

    def __str__(self):
        return f"Payment {self.transaction_id} for Order {self.order.order_ref}"


# testing now


class ProfitMargin(models.Model):
    product = models.ForeignKey(
        "Product", on_delete=models.CASCADE, related_name="profit_margins"
    )
    month = models.PositiveIntegerField()  # Store the month as a number (1-12)
    year = models.PositiveIntegerField()  # Store the year
    total_quantity_sold = models.PositiveIntegerField(default=0)
    total_profit = models.DecimalField(max_digits=10, decimal_places=2, default=0.0)

    class Meta:
        unique_together = (
            "product",
            "month",
            "year",
        )  # Ensure one entry per product per month
        ordering = ["-year", "-month"]  # Show recent records first

    def __str__(self):
        return f"{self.product.name} - {self.month}/{self.year} - Profit: {self.total_profit} BDT"

    @staticmethod
    def update_profit_margin():
        """Recalculate profit margins for the current month."""
        current_date = now()
        month, year = current_date.month, current_date.year

        order_items = OrderItem.objects.filter(
            order__order_date__month=month, order__order_date__year=year
        )

        profit_data = order_items.values("product").annotate(
            total_quantity=Sum("quantity"),
            total_profit=Sum(
                ExpressionWrapper(
                    F("product__profit_margin") * F("quantity"),
                    output_field=DecimalField(max_digits=10, decimal_places=2),
                )
            ),
        )

        for entry in profit_data:
            product = Product.objects.get(id=entry["product"])
            profit_record, created = ProfitMargin.objects.get_or_create(
                product=product,
                month=month,
                year=year,
                defaults={
                    "total_quantity_sold": entry["total_quantity"],
                    "total_profit": entry["total_profit"],
                },
            )
            if not created:
                profit_record.total_quantity_sold = entry["total_quantity"]
                profit_record.total_profit = entry["total_profit"]
                profit_record.save()


class MonthlyTotalProfit(models.Model):
    month = models.PositiveIntegerField()
    year = models.PositiveIntegerField()
    total_profit = models.DecimalField(max_digits=12, decimal_places=2, default=0.0)

    class Meta:
        unique_together = ("month", "year")  # Ensure only one entry per month/year
        ordering = ["-year", "-month"]  # Show recent records first

    def __str__(self):
        return f"Total Profit - {self.month}/{self.year}: {self.total_profit} BDT"

    @staticmethod
    def update_monthly_total_profit():
        """Recalculate total profit for the current month."""
        current_date = now()
        month, year = current_date.month, current_date.year

        total_profit = (
            ProfitMargin.objects.filter(month=month, year=year).aggregate(
                total=Sum("total_profit")
            )["total"]
            or 0.0
        )

        profit_record, created = MonthlyTotalProfit.objects.get_or_create(
            month=month, year=year, defaults={"total_profit": total_profit}
        )

        if not created:
            profit_record.total_profit = total_profit
            profit_record.save()
