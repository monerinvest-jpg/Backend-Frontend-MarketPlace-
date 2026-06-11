# backend/app/services/delivery/cdek.py — реальная реализация

import httpx
from app.core.config import settings
from app.services.delivery.base import DeliveryProvider

_cdek_token_cache: dict = {}


async def _get_cdek_token() -> str:
    """Получить OAuth2 токен CDEK с кешированием"""
    import time
    cached = _cdek_token_cache.get("token")
    expires_at = _cdek_token_cache.get("expires_at", 0)
    
    if cached and time.time() < expires_at - 60:
        return cached
    
    async with httpx.AsyncClient(timeout=10) as client:
        resp = await client.post(
            f"{settings.cdek_api_url}/oauth/token",
            data={
                "grant_type": "client_credentials",
                "client_id": settings.cdek_client_id,
                "client_secret": settings.cdek_client_secret,
            },
        )
        resp.raise_for_status()
        data = resp.json()
    
    _cdek_token_cache["token"] = data["access_token"]
    _cdek_token_cache["expires_at"] = time.time() + data.get("expires_in", 3600)
    return data["access_token"]


class CDEKProvider(DeliveryProvider):
    async def calculate(self, city: str, weight_grams: int) -> dict:
        try:
            token = await _get_cdek_token()
            async with httpx.AsyncClient(timeout=15) as client:
                resp = await client.post(
                    f"{settings.cdek_api_url}/calculator/tariff",
                    headers={"Authorization": f"Bearer {token}"},
                    json={
                        "tariff_code": 136,  # Посылка склад-дверь
                        "from_location": {"city": "Москва"},
                        "to_location": {"city": city},
                        "packages": [{"weight": weight_grams, "length": 20, "width": 20, "height": 10}],
                    },
                )
                resp.raise_for_status()
                data = resp.json()
                return {
                    "service": "cdek",
                    "city": city,
                    "cost": data["total_sum"],
                    "estimated_days": data.get("period_max", 5),
                }
        except Exception as e:
            # Fallback при недоступности API
            return {"service": "cdek", "city": city, "cost": 500, "estimated_days": 7, "warning": "estimated"}