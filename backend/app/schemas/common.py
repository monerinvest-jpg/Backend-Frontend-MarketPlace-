from decimal import Decimal
from pydantic import BaseModel, Field


class OrderItemIn(BaseModel):
    """✅ Типизированная схема элемента заказа"""
    # ⛔ БЫЛО: items: list[dict] — принимал всё что угодно
    product_id: int = Field(gt=0, description="ID товара (должен существовать)")
    quantity: int = Field(ge=1, le=100, description="Количество: от 1 до 100")


class OrderCreateIn(BaseModel):
    address: str = Field(min_length=5, max_length=500, strip_whitespace=True)
    city: str = Field(min_length=2, max_length=100, strip_whitespace=True)
    # ✅ Заменили list[dict] на list[OrderItemIn]
    items: list[OrderItemIn] = Field(min_length=1, max_length=50)


class ProductOut(BaseModel):
    id: int
    title: str
    description: str
    price: Decimal
    status: str
    rating: Decimal
    views_count: int
    
    model_config = {"from_attributes": True}


class PaginationParams(BaseModel):
    """✅ Параметры пагинации для всех списковых запросов"""
    skip: int = Field(0, ge=0, description="Смещение")
    limit: int = Field(20, ge=1, le=100, description="Количество записей")


class SettingIn(BaseModel):
    key: str = Field(min_length=1, max_length=100)
    value: str = Field(max_length=500)