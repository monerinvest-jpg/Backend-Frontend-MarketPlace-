from decimal import Decimal

from app.services.payments.base import PaymentGateway


class CloudPaymentsGateway(PaymentGateway):
    async def create_payment(self, order_id: int, amount: Decimal, return_url: str) -> dict:
        return {
            "status": "stub",
            "gateway": "cloudpayments",
            "order_id": order_id,
            "amount": f"{amount:.2f}",
            "return_url": return_url,
        }

    async def refund_payment(self, payment_id: str, amount: Decimal) -> dict:
        return {"status": "stub", "payment_id": payment_id, "amount": f"{amount:.2f}"}
