from decimal import Decimal

from pydantic import BaseModel


class ProductOut(BaseModel):
    id: int
    title: str
    description: str
    price: Decimal
    status: str


class OrderCreateIn(BaseModel):
    address: str
    city: str
    items: list[dict]


class SettingIn(BaseModel):
    key: str
    value: str
