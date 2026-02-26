from django.urls import path

from payment.views import InitiatePaymentView, PaymentCallbackView

urlpatterns = [
    path("initiate/", InitiatePaymentView.as_view(), name="payment-initiate"),
    path("callback/", PaymentCallbackView.as_view(), name="payment-callback"),
]
