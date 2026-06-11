# backend/app/api/routers/payments.py — новый файл

import hashlib
import hmac
from fastapi import APIRouter, Depends, HTTPException, Request
from app.core.config import settings

router = APIRouter(prefix="/payments", tags=["payments"])

@router.post("/yookassa/webhook")
async def yookassa_webhook(request: Request) -> dict:
    """✅ Обработка webhook с проверкой подписи"""
    
    body = await request.body()
    
    # ✅ Проверка HMAC-SHA256 подписи
    signature = request.headers.get("X-Yookassa-Signature", "")
    if not signature:
        raise HTTPException(status_code=400, detail="Missing signature")
    
    expected = hmac.new(
        settings.yookassa_webhook_secret.encode(),
        body,
        hashlib.sha256
    ).hexdigest()
    
    # ✅ Сравнение через hmac.compare_digest (защита от timing attack)
    if not hmac.compare_digest(expected, signature):
        raise HTTPException(status_code=400, detail="Invalid signature")
    
    event = await request.json()
    event_type = event.get("event")
    
    if event_type == "payment.succeeded":
        payment_id = event["object"]["id"]
        # TODO: обновить статус заказа
    
    return {"status": "ok"}