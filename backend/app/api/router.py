from fastapi import APIRouter

from app.api.routers import admin, auth, orders, products, referrals


api_router = APIRouter(prefix="/api/v1")
api_router.include_router(auth.router)
api_router.include_router(products.router)
api_router.include_router(orders.router)
api_router.include_router(referrals.router)
api_router.include_router(admin.router)
