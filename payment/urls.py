from django.urls import path

from payment.views import (
    CreatePaymentSessionView,
    IPNHandlerView,
    PaymentCancelView,
    PaymentFailView,
    PaymentSuccessView,
)

# from .views import (
#     HomeView,
#     CreatePaymentSessionView,
#     PaymentSuccessView,
#     PaymentFailView,
#     PaymentCancelView,
#     IPNHandlerView
# )

urlpatterns = [
    #     path('', HomeView.as_view(), name='home'),
    path(
        "create-session/<str:order_ref>/",
        CreatePaymentSessionView.as_view(),
        name="create_payment_session",
    ),
    path("success/", PaymentSuccessView.as_view(), name="payment_success"),
    path("fail/", PaymentFailView.as_view(), name="payment_fail"),
    path("cancel/", PaymentCancelView.as_view(), name="payment_cancel"),
    path("ipn/", IPNHandlerView.as_view(), name="ipn_handler"),
]
