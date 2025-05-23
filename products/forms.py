from django import forms
from .models import SHIPPING_CHOICES2


class CheckoutForm(forms.Form):
    recipient_name = forms.CharField(max_length=255, required=True)
    phone_number = forms.CharField(max_length=20, required=True)
    email = forms.EmailField(required=True)
    city = forms.CharField(max_length=100, required=True)
    postal_code = forms.CharField(max_length=20, required=True)
    devary_type = forms.ChoiceField(choices=SHIPPING_CHOICES2, required=True)
    shipping_address = forms.CharField(  # 🚨 Must match model field name
        widget=forms.Textarea(attrs={"rows": 3}), label="Shipping Address"
    )
