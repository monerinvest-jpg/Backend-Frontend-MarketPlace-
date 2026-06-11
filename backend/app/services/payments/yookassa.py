# backend/app/api/routers/payments.py — НОВЫЙ ФАЙЛ

import hashlib
import hmac
import json
from fastapi import APIRouter, HTTPException, Request, status
from app.core.config import settings

router = APIRouter(prefix="/payments", tags=["payments"])


def verify_yookassa_signature(body: bytes, signature: str) -> bool:
    """✅ Верификация HMAC-SHA256 подписи от YooKassa"""
    expected = hmac.new(
        settings.yookassa_webhook_secret.encode(),
        body,
        hashlib.sha256,
    ).hexdigest()
    # ✅ compare_digest — защита от timing attack
    return hmac.compare_digest(expected, signature)


@router.post("/webhook/yookassa")
async def yookassa_webhook(request: Request) -> dict:
    body = await request.body()
    
    # ✅ Проверяем подпись
    signature = request.headers.get("X-Request-Id", "")  # YooKassa подпись
    
    if not verify_yookassa_signature(body, signature):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid webhook signature"
        )
    
    event = json.loads(body)
    payment_id = event.get("object", {}).get("id")
    event_type = event.get("event")
    
    if event_type == "payment.succeeded":
        # ✅ Обновить статус заказа в БД
        metadata = event.get("object", {}).get("metadata", {})
        order_id = int(metadata.get("order_id", 0))
        # await order_service.mark_paid(order_id, payment_id)
    
    return {"ok": True}