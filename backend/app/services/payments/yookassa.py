from decimal import Decimal
from uuid import uuid4

import httpx

from app.core.config import settings
from app.services.payments.base import PaymentGateway


class YooKassaGateway(PaymentGateway):
    base_url = "https://api.yookassa.ru/v3/payments"

    async def create_payment(self, order_id: int, amount: Decimal, return_url: str) -> dict:
        payload = {
            "amount": {"value": f"{amount:.2f}", "currency": "RUB"},
            "capture": True,
            "confirmation": {"type": "redirect", "return_url": return_url},
            "description": f"Order #{order_id}",
            "metadata": {"order_id": str(order_id)},
        }
        headers = {"Idempotence-Key": str(uuid4())}
        async with httpx.AsyncClient(timeout=10) as client:
            response = await client.post(
                self.base_url,
                json=payload,
                headers=headers,
                auth=(settings.yookassa_shop_id, settings.yookassa_secret_key),
            )
        response.raise_for_status()
        return response.json()

    async def refund_payment(self, payment_id: str, amount: Decimal) -> dict:
        payload = {
            "payment_id": payment_id,
            "amount": {"value": f"{amount:.2f}", "currency": "RUB"},
        }
        async with httpx.AsyncClient(timeout=10) as client:
            response = await client.post(
                "https://api.yookassa.ru/v3/refunds",
                json=payload,
                headers={"Idempotence-Key": str(uuid4())},
                auth=(settings.yookassa_shop_id, settings.yookassa_secret_key),
            )
        response.raise_for_status()
        return response.json()
