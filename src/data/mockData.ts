import type { Category, Product, SettingsMap, Shop, User } from "@/types";

export const categories: Category[] = [
  { id: 1, name: "Украшения", slug: "jewelry" },
  { id: 2, name: "Одежда", slug: "fashion" },
  { id: 3, name: "Для дома", slug: "home" },
  { id: 4, name: "Искусство", slug: "art" },
];

export const users: User[] = [
  {
    id: 1,
    email: "root@market.dev",
    fullName: "Super Admin",
    role: "superadmin",
    referralCode: "ROOT001",
    balance: 0,
    isActive: true,
  },
  {
    id: 2,
    email: "seller@market.dev",
    fullName: "Craft Seller",
    role: "seller",
    referralCode: "SELL002",
    balance: 17400,
    isActive: true,
  },
  {
    id: 3,
    email: "buyer@market.dev",
    fullName: "Buyer Demo",
    role: "buyer",
    referralCode: "BUY003",
    balance: 840,
    isActive: true,
  },
];

export const shops: Shop[] = [
  {
    id: 1,
    ownerId: 2,
    name: "Northern Craft",
    description: "Ручная работа от локальных мастеров",
    commissionPercent: null,
    rating: 4.8,
    isActive: true,
  },
];

export const products: Product[] = [
  {
    id: 1,
    shopId: 1,
    categoryId: 1,
    title: "Серебряное кольцо Aurora",
    description: "Авторское кольцо из серебра 925 пробы",
    price: 5900,
    quantity: 15,
    status: "active",
    rating: 4.9,
    viewsCount: 1200,
    imageUrl:
      "https://images.unsplash.com/photo-1611652022419-a9419f74343d?auto=format&fit=crop&w=1200&q=80",
  },
  {
    id: 2,
    shopId: 1,
    categoryId: 3,
    title: "Керамическая ваза Fjord",
    description: "Матовая керамика с ручной глазурью",
    price: 4200,
    quantity: 9,
    status: "active",
    rating: 4.7,
    viewsCount: 650,
    imageUrl:
      "https://images.unsplash.com/photo-1612196808214-b7e239e5f2f0?auto=format&fit=crop&w=1200&q=80",
  },
  {
    id: 3,
    shopId: 1,
    categoryId: 2,
    title: "Льняная рубашка Atelier",
    description: "Свободный крой, 100% лен",
    price: 6800,
    quantity: 24,
    status: "pending",
    rating: 4.6,
    viewsCount: 210,
    imageUrl:
      "https://images.unsplash.com/photo-1489987707025-afc232f7ea0f?auto=format&fit=crop&w=1200&q=80",
  },
];

export const defaultSettings: SettingsMap = {
  global_commission_percent: 10,
  referral_buyer_bonus_amount: 300,
  referral_buyer_min_order_amount: 2500,
  referral_seller_bonus_amount: 1500,
  referral_bonus_max_discount_percent: 30,
  enable_premoderation: true,
  yookassa_shop_id: "demo-shop-id",
  yookassa_secret_key: "demo-secret",
  cdek_client_id: "demo-client-id",
  cdek_client_secret: "demo-client-secret",
};
