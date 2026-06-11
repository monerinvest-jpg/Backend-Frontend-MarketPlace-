from abc import ABC, abstractmethod
from decimal import Decimal


class PaymentGateway(ABC):
    @abstractmethod
    async def create_payment(self, order_id: int, amount: Decimal, return_url: str) -> dict:
        raise NotImplementedError

    @abstractmethod
    async def refund_payment(self, payment_id: str, amount: Decimal) -> dict:
        raise NotImplementedError
