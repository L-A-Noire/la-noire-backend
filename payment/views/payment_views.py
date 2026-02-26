import requests
from django.conf import settings
from django.shortcuts import redirect
from django.views import View
from drf_spectacular.utils import OpenApiResponse, extend_schema
from rest_framework import status
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework.views import APIView

from payment.models import Transaction
from payment.serializers import (
    InitiatePaymentResponseSerializer,
    PaymentErrorSerializer,
    TransactionCreateSerializer,
)

BITPAY_GATEWAY_SEND = "https://bitpay.ir/payment-test/gateway-send"
BITPAY_GATEWAY_URL = "https://bitpay.ir/payment-test/gateway-{id_get}-get"
BITPAY_GATEWAY_RESULT = "https://bitpay.ir/payment-test/gateway-result-second"


class InitiatePaymentView(APIView):
    permission_classes = [AllowAny]

    @extend_schema(
        summary="Initiate a payment",
        description="Creates a transaction and returns the BitPay gateway URL "
        "to redirect the user for payment.",
        request=TransactionCreateSerializer,
        responses={
            200: OpenApiResponse(
                response=InitiatePaymentResponseSerializer,
                description="Gateway URL to redirect user to",
            ),
            502: OpenApiResponse(
                response=PaymentErrorSerializer,
                description="Payment gateway error",
            ),
        },
        tags=["Payment"],
    )
    def post(self, request):
        serializer = TransactionCreateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        data = serializer.validated_data
        transaction = Transaction.objects.create(
            amount=data["amount"],
            mobile_num=data.get("mobile_num", ""),
            description=data.get("description", ""),
        )

        callback_url = request.build_absolute_uri("/api/payment/callback/")

        payload = {
            "api": settings.BITPAY_API_KEY,
            "amount": transaction.amount,
            "redirect": callback_url,
            "name": "LA-Noire",
            "description": "Payment for LA-Noire",
            "mobileNum": data.get("mobile_num", ""),
            "factorId": str(transaction.factor_id),
        }

        try:
            response = requests.post(BITPAY_GATEWAY_SEND, data=payload, timeout=15)
            print(BITPAY_GATEWAY_SEND)
            print(payload)
            id_get = response.text.strip()
            print(id_get)
            if not id_get or int(id_get) <= 0:
                transaction.delete()
                return Response(
                    {"error": "Payment gateway returned an invalid response."},
                    status=status.HTTP_502_BAD_GATEWAY,
                )

            transaction.id_get = id_get
            transaction.save(update_fields=["id_get"])

            gateway_url = BITPAY_GATEWAY_URL.format(id_get=id_get)

            return Response(
                {"gateway_url": gateway_url},
                status=status.HTTP_200_OK,
            )

        except (requests.RequestException, ValueError):
            transaction.delete()
            return Response(
                {"error": "Could not connect to payment gateway."},
                status=status.HTTP_502_BAD_GATEWAY,
            )


@extend_schema(exclude=True)
class PaymentCallbackView(View):
    """Plain Django view that BitPay redirects the user back to."""

    def get(self, request):
        trans_id = request.GET.get("trans_id", "")
        id_get = request.GET.get("id_get", "")
        factor_id = request.GET.get("factorId", "")

        transaction = Transaction.objects.filter(factor_id=factor_id).first()
        if not transaction:
            return redirect(f"{settings.FRONTEND_URL}/failed-payment")

        transaction.trans_id = trans_id
        transaction.save(update_fields=["trans_id"])

        payload = {
            "api": settings.BITPAY_API_KEY,
            "trans_id": trans_id,
            "id_get": id_get,
            "json": 1,
        }

        try:
            response = requests.post(BITPAY_GATEWAY_RESULT, data=payload, timeout=15)
            result = response.json()
        except (requests.RequestException, ValueError):
            return redirect(f"{settings.FRONTEND_URL}/failed-payment")

        if result.get("status") == 1:
            transaction.is_success = True
            transaction.amount = result.get("amount", transaction.amount)
            transaction.card_number = result.get("cardNum", "")
            transaction.save(update_fields=["is_success", "amount", "card_number"])

            return redirect(
                f"{settings.FRONTEND_URL}/success-payment"
                f"?amount={transaction.amount}&factorId={transaction.factor_id}"
            )

        return redirect(f"{settings.FRONTEND_URL}/failed-payment")
