from django.shortcuts import render, redirect
from django.views.generic import TemplateView, View
from django.http import HttpResponse
from sslcommerz_lib import SSLCOMMERZ
from django.conf import settings
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt, csrf_protect
from django.middleware.csrf import get_token
from products.models import Order, Payment
import uuid
import logging
from django.utils import timezone
from django.core.mail import send_mail

# Set up logging
logger = logging.getLogger(__name__)


class HomeView(TemplateView):
    template_name = "home.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["title"] = "Payment System"
        # Force CSRF token creation
        get_token(self.request)
        return context


@method_decorator(csrf_exempt, name="dispatch")
class CreatePaymentSessionView(View):
    def post(self, request, *args, **kwargs):
        order_ref = kwargs.get("order_ref")  # Extract order_ref from URL parameters
        return self._process_payment(request, order_ref)

    def get(self, request, *args, **kwargs):
        order_ref = kwargs.get("order_ref")  # Extract order_ref from URL parameters
        return self._process_payment(request, order_ref)

    def _process_payment(self, request, order_ref, *args, **kwargs):
        sslcz = SSLCOMMERZ(settings.SSLCOMMERZ_SETTINGS)

        try:
            order = Order.objects.get(order_ref=order_ref)
        except Order.DoesNotExist:
            logger.error(f"Order not found for ref: {order_ref}")
            return HttpResponse("Invalid order reference", status=404)

        transaction_id = str(uuid.uuid4().hex)[:10]

        success_url = request.build_absolute_uri(
            f"/payment/success/?order_ref={order_ref}&tran_id={transaction_id}"
        )
        fail_url = request.build_absolute_uri("/payment/fail/")
        cancel_url = request.build_absolute_uri("/payment/cancel/")

        post_body = {
            "total_amount": order.total_amount,
            "currency": "BDT",
            "tran_id": transaction_id,
            "success_url": success_url,
            "fail_url": fail_url,
            "cancel_url": cancel_url,
            "emi_option": 0,
            "cus_name": order.recipient_name or "Default Name",  # Default value if None
            "cus_email": order.email or "default@example.com",  # Default value if None
            "cus_phone": order.phone_number or "0123456789",  # Default value if None
            "cus_add1": order.shipping_address
            or "Default Address",  # Default value if None
            "cus_city": order.city or "Default City",  # Default value if None
            "cus_country": "Bangladesh",
            "shipping_method": order.devary_type
            or "Default Method",  # Default value if None
            "multi_card_name": "",
            "num_of_item": 1,
            "product_name": "Order " + order.order_ref,
            "product_category": "categories",
            "product_profile": "general",
            # Add the missing fields
            "ship_name": order.recipient_name
            or "Default Name",  # Default value if None
            "ship_add1": order.shipping_address
            or "Default Address",  # Default value if None
            "ship_city": order.city
            or "Default City",  # Add the missing ship_city field
            "ship_country": "Bangladesh",
            "ship_postcode": order.postal_code
            or "1234",  # Add the missing ship_postcode field
        }

        try:
            response = sslcz.createSession(post_body)
            logger.info(f"Payment session response: {response}")

            if response.get("status") == "SUCCESS" and "GatewayPageURL" in response:
                order.transaction_id = transaction_id
                order.save()
                return redirect(response["GatewayPageURL"])
            else:
                error_msg = response.get(
                    "failedreason", "Payment initialization failed"
                )
                logger.error(f"Payment initialization failed: {error_msg}")
                return HttpResponse(
                    f"Payment initialization failed: {error_msg}", status=400
                )
        except Exception as e:
            logger.error(f"Payment processing error: {str(e)}")
            return HttpResponse(
                f"Error during payment processing: {str(e)}", status=500
            )


@method_decorator(csrf_exempt, name="dispatch")
class PaymentSuccessView(TemplateView):
    template_name = "payment/success.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        data = (
            self.request.POST.dict()
            if self.request.method == "POST"
            else self.request.GET.dict()
        )

        tran_id = data.get("tran_id")
        val_id = data.get("val_id")

        if not tran_id or not val_id:
            logger.error("Missing transaction data")
            return HttpResponse("Missing transaction data", status=400)

        try:
            order = Order.objects.get(transaction_id=tran_id)
        except Order.DoesNotExist:
            logger.error(f"Invalid transaction ID: {tran_id}")
            return HttpResponse("Invalid transaction ID", status=404)

        sslcz = SSLCOMMERZ(settings.SSLCOMMERZ_SETTINGS)
        try:
            validation_response = sslcz.validationTransactionOrder(val_id)
        except Exception as e:
            logger.error(f"Validation failed: {str(e)}")
            return HttpResponse(f"Payment validation failed: {str(e)}", status=500)

        payment_status = data.get("status")

        # Update Order and Create Payment Entry
        if validation_response.get("status") == "VALID" and payment_status == "VALID":
            order.payment_status = "paid"
            order.transaction_id = tran_id
            order.payment_method = data.get("card_type", "Unknown")
            order.save()

            # Create Payment entry
            payment, created = Payment.objects.get_or_create(
                order=order,
                transaction_id=tran_id,
                defaults={
                    "validation_id": val_id,
                    "bank_transaction_id": data.get("bank_tran_id", ""),
                    "amount": data.get("amount", 0),
                    "currency": data.get("currency", "BDT"),
                    "card_type": data.get("card_type", ""),
                    "card_brand": data.get("card_brand", ""),
                    "card_issuer": data.get("card_issuer", ""),
                    "card_issuer_country": data.get("card_issuer_country", ""),
                    "payment_status": "valid",
                    "transaction_date": data.get("tran_date", timezone.now()),
                },
            )

            if not created:
                logger.info(f"Payment entry already exists for order {order.order_ref}")

            logger.info(f"Payment successful for order: {order.order_ref}")

            # Trigger payment success signal
            from payment.signals import payment_success_signal

            payment_success_signal.send(sender=self.__class__, order=order)

        context.update(
            {
                "order": order,
                "order_items": order.order_items.all(),
                "payment_data": data,
                "payment_info": {
                    "transaction_id": tran_id,
                    "amount": data.get("amount", ""),
                    "currency": data.get("currency", "BDT"),
                    "payment_status": payment_status,
                    "validation_response": validation_response,
                    "card_type": data.get("card_type", ""),
                    "bank_transaction_id": data.get("bank_tran_id", ""),
                    "transaction_date": data.get("tran_date", ""),
                    "phone_number": order.phone_number,  # Add phone number from order
                    "email": order.email,  # Add email from order
                },
            }
        )
        return context

    def post(self, request, *args, **kwargs):
        return self.render_to_response(self.get_context_data(**kwargs))


@method_decorator(csrf_exempt, name="dispatch")
class PaymentFailView(TemplateView):
    template_name = "payment/fail.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["payment_data"] = self.request.GET
        return context

    def post(self, request, *args, **kwargs):
        # Handle POST requests from payment gateway
        context = self.get_context_data(**kwargs)
        context["payment_data"] = request.POST
        return self.render_to_response(context)


@method_decorator(csrf_exempt, name="dispatch")
class PaymentCancelView(TemplateView):
    template_name = "payment/cancel.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["payment_data"] = self.request.GET
        return context

    def post(self, request, *args, **kwargs):
        # Handle POST requests from payment gateway
        context = self.get_context_data(**kwargs)
        context["payment_data"] = request.POST
        return self.render_to_response(context)


@method_decorator(csrf_exempt, name="dispatch")
class IPNHandlerView(View):
    def post(self, request, *args, **kwargs):
        sslcz = SSLCOMMERZ(settings.SSLCOMMERZ_SETTINGS)
        post_body = request.POST.dict()

        try:
            if sslcz.hash_validate_ipn(post_body):
                response = sslcz.validationTransactionOrder(post_body["val_id"])
                print("Transaction Validated:", response)
                return HttpResponse("IPN Validation Successful")
            else:
                print("Hash validation failed")
                return HttpResponse("IPN Validation Failed")
        except Exception as e:
            print(f"IPN Error: {str(e)}")
            return HttpResponse(f"IPN Error: {str(e)}")

    def get(self, request, *args, **kwargs):
        return HttpResponse("Invalid Request")
