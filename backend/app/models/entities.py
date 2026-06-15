from decimal import Decimal
from enum import Enum

from sqlalchemy import Boolean, Enum as SQLEnum, ForeignKey, Index, Numeric, String, Text
from sqlalchemy.orm import Mapped, mapped_column

from app.models.base import Base, TimestampMixin


class RoleEnum(str, Enum):
    SUPERADMIN = "superadmin"
    MODERATOR = "moderator"
    SELLER = "seller"
    BUYER = "buyer"


class ProductStatus(str, Enum):
    PENDING = "pending"
    ACTIVE = "active"
    REJECTED = "rejected"
    BLOCKED = "blocked"


class OrderStatus(str, Enum):
    PENDING_PAYMENT = "pending_payment"
    PAID = "paid"
    PROCESSING = "processing"
    SHIPPED = "shipped"
    DELIVERED = "delivered"
    COMPLETED = "completed"
    CANCELLED = "cancelled"
    REFUNDED = "refunded"


class ReferralType(str, Enum):
    BUYER = "buyer"
    SELLER = "seller"


class User(TimestampMixin, Base):
    __tablename__ = "user"

    id: Mapped[int] = mapped_column(primary_key=True)
    email: Mapped[str] = mapped_column(String(255), unique=True, index=True)
    password_hash: Mapped[str] = mapped_column(String(255))
    phone: Mapped[str | None] = mapped_column(String(30), nullable=True)
    full_name: Mapped[str] = mapped_column(String(255))
    role: Mapped[RoleEnum] = mapped_column(SQLEnum(RoleEnum), default=RoleEnum.BUYER)
    referral_code: Mapped[str] = mapped_column(String(20), unique=True, index=True)
    balance: Mapped[Decimal] = mapped_column(Numeric(12, 2), default=0)
    is_superuser: Mapped[bool] = mapped_column(Boolean, default=False)
    is_staff: Mapped[bool] = mapped_column(Boolean, default=False)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)


class Shop(TimestampMixin, Base):
    __tablename__ = "shop"

    id: Mapped[int] = mapped_column(primary_key=True)
    owner_id: Mapped[int] = mapped_column(ForeignKey("user.id"), index=True)
    name: Mapped[str] = mapped_column(String(255), index=True)
    description: Mapped[str] = mapped_column(Text)
    logo_url: Mapped[str | None] = mapped_column(String(500), nullable=True)
    commission_percent: Mapped[Decimal | None] = mapped_column(Numeric(5, 2), nullable=True)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    rating: Mapped[Decimal] = mapped_column(Numeric(3, 2), default=0)


class Category(Base):
    __tablename__ = "category"

    id: Mapped[int] = mapped_column(primary_key=True)
    parent_id: Mapped[int | None] = mapped_column(ForeignKey("category.id"), nullable=True, index=True)
    name: Mapped[str] = mapped_column(String(255), index=True)
    slug: Mapped[str] = mapped_column(String(255), unique=True)
    image: Mapped[str | None] = mapped_column(String(500), nullable=True)


class Product(TimestampMixin, Base):
    __tablename__ = "product"

    id: Mapped[int] = mapped_column(primary_key=True)
    shop_id: Mapped[int] = mapped_column(ForeignKey("shop.id"), index=True)
    category_id: Mapped[int] = mapped_column(ForeignKey("category.id"), index=True)
    title: Mapped[str] = mapped_column(String(255), index=True)
    description: Mapped[str] = mapped_column(Text)
    price: Mapped[Decimal] = mapped_column(Numeric(12, 2))
    compare_at_price: Mapped[Decimal | None] = mapped_column(Numeric(12, 2), nullable=True)
    quantity: Mapped[int] = mapped_column(default=0)
    status: Mapped[ProductStatus] = mapped_column(SQLEnum(ProductStatus), default=ProductStatus.PENDING, index=True)
    moderation_reason: Mapped[str | None] = mapped_column(Text, nullable=True)
    rating: Mapped[Decimal] = mapped_column(Numeric(3, 2), default=0)
    views_count: Mapped[int] = mapped_column(default=0)


class ProductImage(Base):
    __tablename__ = "product_image"

    id: Mapped[int] = mapped_column(primary_key=True)
    product_id: Mapped[int] = mapped_column(ForeignKey("product.id"), index=True)
    url: Mapped[str] = mapped_column(String(500))
    is_main: Mapped[bool] = mapped_column(Boolean, default=False)


class CartItem(Base):
    __tablename__ = "cart_item"

    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("user.id"), index=True)
    product_id: Mapped[int] = mapped_column(ForeignKey("product.id"), index=True)
    quantity: Mapped[int] = mapped_column(default=1)


class Order(TimestampMixin, Base):
    __tablename__ = "orders"

    id: Mapped[int] = mapped_column(primary_key=True)
    buyer_id: Mapped[int] = mapped_column(ForeignKey("user.id"), index=True)
    total_price: Mapped[Decimal] = mapped_column(Numeric(12, 2))
    subtotal: Mapped[Decimal] = mapped_column(Numeric(12, 2))
    delivery_cost: Mapped[Decimal] = mapped_column(Numeric(12, 2), default=0)
    platform_fee: Mapped[Decimal] = mapped_column(Numeric(12, 2), default=0)
    commission_percent_used: Mapped[Decimal] = mapped_column(Numeric(5, 2), default=0)
    status: Mapped[OrderStatus] = mapped_column(SQLEnum(OrderStatus), default=OrderStatus.PENDING_PAYMENT, index=True)
    delivery_address: Mapped[str] = mapped_column(Text)


class OrderItem(Base):
    __tablename__ = "order_item"

    id: Mapped[int] = mapped_column(primary_key=True)
    order_id: Mapped[int] = mapped_column(ForeignKey("orders.id"), index=True)
    product_id: Mapped[int] = mapped_column(ForeignKey("product.id"), index=True)
    quantity: Mapped[int] = mapped_column(default=1)
    price_at_time: Mapped[Decimal] = mapped_column(Numeric(12, 2))


class Payment(Base):
    __tablename__ = "payment"

    id: Mapped[int] = mapped_column(primary_key=True)
    order_id: Mapped[int] = mapped_column(ForeignKey("orders.id"), index=True)
    gateway: Mapped[str] = mapped_column(String(50), index=True)
    gateway_payment_id: Mapped[str] = mapped_column(String(255), index=True)
    amount: Mapped[Decimal] = mapped_column(Numeric(12, 2))
    status: Mapped[str] = mapped_column(String(50), index=True)
    paid_at: Mapped[str | None] = mapped_column(String(50), nullable=True)


class Transaction(Base):
    __tablename__ = "transaction"

    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("user.id"), index=True)
    type: Mapped[str] = mapped_column(String(50), index=True)
    amount: Mapped[Decimal] = mapped_column(Numeric(12, 2))
    order_id: Mapped[int | None] = mapped_column(ForeignKey("orders.id"), nullable=True, index=True)
    description: Mapped[str] = mapped_column(Text)
    balance_after: Mapped[Decimal] = mapped_column(Numeric(12, 2), default=0)


class DeliveryInfo(Base):
    __tablename__ = "delivery_info"

    id: Mapped[int] = mapped_column(primary_key=True)
    order_id: Mapped[int] = mapped_column(ForeignKey("orders.id"), index=True)
    delivery_service: Mapped[str] = mapped_column(String(50), default="cdek")
    tracking_number: Mapped[str | None] = mapped_column(String(100), nullable=True, index=True)
    cost: Mapped[Decimal] = mapped_column(Numeric(12, 2), default=0)
    estimated_days: Mapped[int] = mapped_column(default=3)
    city: Mapped[str] = mapped_column(String(255))
    address: Mapped[str] = mapped_column(Text)


class Referral(Base):
    __tablename__ = "referral"

    id: Mapped[int] = mapped_column(primary_key=True)
    referrer_id: Mapped[int] = mapped_column(ForeignKey("user.id"), index=True)
    referred_user_id: Mapped[int] = mapped_column(ForeignKey("user.id"), index=True)
    type: Mapped[ReferralType] = mapped_column(SQLEnum(ReferralType), index=True)
    code: Mapped[str] = mapped_column(String(20), index=True)
    reward_paid: Mapped[bool] = mapped_column(Boolean, default=False)


class ReferralReward(Base):
    __tablename__ = "referral_reward"

    id: Mapped[int] = mapped_column(primary_key=True)
    referral_id: Mapped[int] = mapped_column(ForeignKey("referral.id"), index=True)
    amount: Mapped[Decimal] = mapped_column(Numeric(12, 2))
    type: Mapped[str] = mapped_column(String(50))
    status: Mapped[str] = mapped_column(String(50), default="pending")


class BalanceTransaction(Base):
    __tablename__ = "balance_transaction"

    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("user.id"), index=True)
    change: Mapped[Decimal] = mapped_column(Numeric(12, 2))
    type: Mapped[str] = mapped_column(String(50), index=True)
    reference_type: Mapped[str] = mapped_column(String(50))
    reference_id: Mapped[int] = mapped_column(index=True)


class Report(TimestampMixin, Base):
    __tablename__ = "report"

    id: Mapped[int] = mapped_column(primary_key=True)
    reporter_id: Mapped[int] = mapped_column(ForeignKey("user.id"), index=True)
    target_type: Mapped[str] = mapped_column(String(50), index=True)
    target_id: Mapped[int] = mapped_column(index=True)
    reason: Mapped[str] = mapped_column(Text)
    status: Mapped[str] = mapped_column(String(50), default="new", index=True)
    moderator_id: Mapped[int | None] = mapped_column(ForeignKey("user.id"), nullable=True, index=True)
    resolution: Mapped[str | None] = mapped_column(Text, nullable=True)


class Review(TimestampMixin, Base):
    __tablename__ = "review"

    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("user.id"), index=True)
    product_id: Mapped[int] = mapped_column(ForeignKey("product.id"), index=True)
    rating: Mapped[int] = mapped_column(default=5)
    text: Mapped[str] = mapped_column(Text)


class Coupon(Base):
    __tablename__ = "coupon"

    id: Mapped[int] = mapped_column(primary_key=True)
    code: Mapped[str] = mapped_column(String(50), unique=True, index=True)
    discount_type: Mapped[str] = mapped_column(String(20))
    discount_value: Mapped[Decimal] = mapped_column(Numeric(12, 2))
    valid_from: Mapped[str] = mapped_column(String(50))
    valid_until: Mapped[str] = mapped_column(String(50))
    max_uses: Mapped[int] = mapped_column(default=0)
    used_count: Mapped[int] = mapped_column(default=0)


class Favorite(Base):
    __tablename__ = "favorite"

    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("user.id"), index=True)
    product_id: Mapped[int] = mapped_column(ForeignKey("product.id"), index=True)


class Settings(Base):
    __tablename__ = "settings"

    key: Mapped[str] = mapped_column(String(150), primary_key=True)
    value: Mapped[str] = mapped_column(Text)


Index("ix_product_text", Product.title, Product.description)

class BalanceTransaction(Base):
    __tablename__ = "balance_transaction"
    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("user.id"), index=True)
    amount: Mapped[Decimal] = mapped_column(Numeric(12, 2))
    type: Mapped[str] = mapped_column(String(50))
    description: Mapped[str] = mapped_column(Text)

class Review(TimestampMixin, Base):
    __tablename__ = "review"
    id: Mapped[int] = mapped_column(primary_key=True)
    product_id: Mapped[int] = mapped_column(ForeignKey("product.id"), index=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("user.id"), index=True)
    rating: Mapped[int] = mapped_column()
    text: Mapped[str | None] = mapped_column(Text, nullable=True)

class Coupon(Base):
    __tablename__ = "coupon"
    id: Mapped[int] = mapped_column(primary_key=True)
    code: Mapped[str] = mapped_column(String(50), unique=True, index=True)
    discount_percent: Mapped[Decimal] = mapped_column(Numeric(5, 2))
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)

class Favorite(Base):
    __tablename__ = "favorite"
    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("user.id"), index=True)
    product_id: Mapped[int] = mapped_column(ForeignKey("product.id"), index=True)

class Report(Base):
    __tablename__ = "report"
    id: Mapped[int] = mapped_column(primary_key=True)
    reporter_id: Mapped[int] = mapped_column(ForeignKey("user.id"), index=True)
    product_id: Mapped[int] = mapped_column(ForeignKey("product.id"), nullable=True)
    reason: Mapped[str] = mapped_column(Text)

class Settings(Base):
    __tablename__ = "settings"
    id: Mapped[int] = mapped_column(primary_key=True)
    key: Mapped[str] = mapped_column(String(100), unique=True, index=True)
    value: Mapped[str] = mapped_column(String(500))