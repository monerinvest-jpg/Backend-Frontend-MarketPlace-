export type UserRole = "superadmin" | "moderator" | "seller" | "buyer";

export type ProductStatus = "pending" | "active" | "rejected" | "blocked";

export interface User {
  id: number;
  email: string;
  fullName: string;
  role: UserRole;
  referralCode: string;
  balance: number;
  isActive: boolean;
}

export interface Shop {
  id: number;
  ownerId: number;
  name: string;
  description: string;
  commissionPercent: number | null;
  rating: number;
  isActive: boolean;
}

export interface Category {
  id: number;
  name: string;
  slug: string;
}

export interface Product {
  id: number;
  shopId: number;
  categoryId: number;
  title: string;
  description: string;
  price: number;
  quantity: number;
  status: ProductStatus;
  rating: number;
  viewsCount: number;
  imageUrl: string;
}

export interface CartItem {
  productId: number;
  quantity: number;
}

export type OrderStatus =
  | "pending_payment"
  | "paid"
  | "processing"
  | "shipped"
  | "delivered"
  | "completed"
  | "cancelled"
  | "refunded";

export interface Order {
  id: number;
  buyerId: number;
  totalPrice: number;
  subtotal: number;
  deliveryCost: number;
  platformFee: number;
  commissionPercentUsed: number;
  status: OrderStatus;
  createdAt: string;
}

export interface SettingsMap {
  global_commission_percent: number;
  referral_buyer_bonus_amount: number;
  referral_buyer_min_order_amount: number;
  referral_seller_bonus_amount: number;
  referral_bonus_max_discount_percent: number;
  enable_premoderation: boolean;
  yookassa_shop_id: string;
  yookassa_secret_key: string;
  cdek_client_id: string;
  cdek_client_secret: string;
}
