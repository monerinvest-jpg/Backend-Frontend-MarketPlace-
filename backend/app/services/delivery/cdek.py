from app.services.delivery.base import DeliveryProvider


class CDEKProvider(DeliveryProvider):
    async def calculate(self, city: str, weight_grams: int) -> dict:
        base = 290 if city.lower() == "москва" else 450
        dynamic = int(weight_grams / 1000) * 80
        cost = base + dynamic
        return {"service": "cdek", "city": city, "cost": cost, "estimated_days": 2 if base == 290 else 5}

    async def track(self, tracking_number: str) -> dict:
        return {"tracking_number": tracking_number, "status": "in_transit"}
