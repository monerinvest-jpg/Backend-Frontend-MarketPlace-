from app.services.delivery.base import DeliveryProvider


class BoxberryProvider(DeliveryProvider):
    async def calculate(self, city: str, weight_grams: int) -> dict:
        return {
            "service": "boxberry",
            "city": city,
            "cost": 350 + int(weight_grams / 1000) * 60,
            "estimated_days": 4,
        }

    async def track(self, tracking_number: str) -> dict:
        return {"tracking_number": tracking_number, "status": "accepted"}
