# payments/utils.py

import logging
from django.conf import settings
from sslcommerz_lib import SSLCOMMERZ
from products.models import Order, Payment
from django.utils import timezone

logger = logging.getLogger(__name__)

def process_payment_success(data):
    tran_id = data.get('tran_id')
    val_id = data.get('val_id')

    if not tran_id or not val_id:
        logger.error("Missing transaction data")
        return None, HttpResponse("Missing transaction data", status=400)

    try:
        order = Order.objects.get(transaction_id=tran_id)
    except Order.DoesNotExist:
        logger.error(f"Invalid transaction ID: {tran_id}")
        return None, HttpResponse("Invalid transaction ID", status=404)

    sslcz = SSLCOMMERZ(settings.SSLCOMMERZ_SETTINGS)
    try:
        validation_response = sslcz.validationTransactionOrder(val_id)
    except Exception as e:
        logger.error(f"Validation failed: {str(e)}")
        return None, HttpResponse(f"Payment validation failed: {str(e)}", status=500)

    payment_status = data.get('status')

    if validation_response.get('status') == 'VALID' and payment_status == 'VALID':
        order.payment_status = 'paid'
        order.transaction_id = tran_id
        order.payment_method = data.get('card_type', 'Unknown')
        order.save()

        # Create Payment entry if it doesn't exist
        payment, created = Payment.objects.get_or_create(
            order=order,
            transaction_id=tran_id,
            defaults={
                'validation_id': val_id,
                'bank_transaction_id': data.get('bank_tran_id', ''),
                'amount': data.get('amount', 0),
                'currency': data.get('currency', 'BDT'),
                'card_type': data.get('card_type', ''),
                'card_brand': data.get('card_brand', ''),
                'card_issuer': data.get('card_issuer', ''),
                'card_issuer_country': data.get('card_issuer_country', ''),
                'payment_status': 'valid',
                'transaction_date': data.get('tran_date', timezone.now()),
            }
        )

        if not created:
            logger.info(f"Payment entry already exists for order {order.order_ref}")

        logger.info(f"Payment successful for order: {order.order_ref}")

    return order, validation_response