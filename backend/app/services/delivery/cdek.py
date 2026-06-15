# backend/app/services/delivery/cdek.py — asyncio.Lock + retry

import asyncio
import time
import httpx
from app.core.config import settings
from app.services.delivery.base import DeliveryProvider

_cdek_token_cache: dict = {}
_cdek_lock = asyncio.Lock()   # ✅ Защита от race condition


async def _get_cdek_token() -> str:
    """Получить OAuth2 токен CDEK с кешированием и защитой от race condition"""
    async with _cdek_lock:    # ✅ Только одна coroutine обновляет токен
        cached = _cdek_token_cache.get("token")
        expires_at = _cdek_token_cache.get("expires_at", 0)
        if cached and time.time() < expires_at - 60:
            return cached

        # ✅ Retry с exponential backoff (1s, 2s, 4s)
        last_exc: Exception | None = None
        for attempt in range(3):
            try:
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
            except Exception as exc:
                last_exc = exc
                if attempt < 2:
                    await asyncio.sleep(2 ** attempt)

        raise RuntimeError(f"CDEK auth failed after 3 retries: {last_exc}")


class CDEKProvider(DeliveryProvider):
    async def calculate(self, city: str, weight_grams: int) -> dict:
        try:
            token = await _get_cdek_token()
            async with httpx.AsyncClient(timeout=15) as client:
                resp = await client.post(
                    f"{settings.cdek_api_url}/calculator/tariff",
                    headers={"Authorization": f"Bearer {token}"},
                    json={
                        "tariff_code": 136,
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
        except Exception:
            # Fallback при недоступности API
            return {"service": "cdek", "city": city, "cost": 500, "estimated_days": 7, "warning": "estimated"}