# backend/tests/test_auth.py — пример минимального теста

import pytest
from httpx import AsyncClient, ASGITransport
from app.main import app

@pytest.mark.asyncio
async def test_register_success():
    async with AsyncClient(
        transport=ASGITransport(app=app), base_url="http://test"
    ) as ac:
        response = await ac.post("/api/v1/auth/register", json={
            "email": "test@example.com",
            "password": "SecurePass123!",
            "full_name": "Test User",
        })
    assert response.status_code == 201
    data = response.json()
    assert "access_token" in data
    assert "refresh_token" in data

@pytest.mark.asyncio
async def test_register_duplicate_email():
    # Второй запрос с тем же email должен вернуть 409
    ...

@pytest.mark.asyncio
async def test_login_wrong_password():
    async with AsyncClient(...) as ac:
        response = await ac.post("/api/v1/auth/login", json={
            "email": "test@example.com",
            "password": "WrongPassword",
        })
    assert response.status_code == 401
    # ✅ Проверяем что сообщение одинаково (не раскрывает наличие email)
    assert response.json()["detail"] == "Неверный email или пароль"