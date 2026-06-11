from abc import ABC, abstractmethod


class DeliveryProvider(ABC):
    @abstractmethod
    async def calculate(self, city: str, weight_grams: int) -> dict:
        raise NotImplementedError

    @abstractmethod
    async def track(self, tracking_number: str) -> dict:
        raise NotImplementedError
