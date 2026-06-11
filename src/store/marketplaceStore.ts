import { create } from "zustand";
import { persist } from "zustand/middleware";
import { categories, defaultSettings, products, shops } from "@/data/mockData";
import type { CartItem, Order, OrderStatus, Product, ProductStatus, SettingsMap, Shop } from "@/types";

interface MarketplaceState {
  categories: typeof categories;
  shops: Shop[];
  products: Product[];
  cart: CartItem[];
  favorites: number[];
  orders: Order[];
  settings: SettingsMap;
  addToCart: (productId: number) => void;
  updateCartQuantity: (productId: number, quantity: number) => void;
  removeFromCart: (productId: number) => void;
  toggleFavorite: (productId: number) => void;
  clearCart: () => void;
  createOrder: (buyerId: number, deliveryCost: number) => Order | null;
  updateOrderStatus: (orderId: number, status: OrderStatus) => void;
  updateProductStatus: (productId: number, status: ProductStatus) => void;
  updateShopCommission: (shopId: number, commissionPercent: number | null) => void;
  updateSetting: <K extends keyof SettingsMap>(key: K, value: SettingsMap[K]) => void;
}

const nextOrderId = (ordersList: Order[]) => {
  if (ordersList.length === 0) return 1;
  return Math.max(...ordersList.map((order) => order.id)) + 1;
};

export const useMarketplaceStore = create<MarketplaceState>()(
  persist(
    (set, get) => ({
      categories,
      shops,
      products,
      cart: [],
      favorites: [],
      orders: [],
      settings: defaultSettings,
      addToCart: (productId) => {
        set((state) => {
          const current = state.cart.find((item) => item.productId === productId);
          if (current) {
            return {
              cart: state.cart.map((item) =>
                item.productId === productId ? { ...item, quantity: item.quantity + 1 } : item
              ),
            };
          }
          return { cart: [...state.cart, { productId, quantity: 1 }] };
        });
      },
      updateCartQuantity: (productId, quantity) => {
        if (quantity <= 0) {
          get().removeFromCart(productId);
          return;
        }
        set((state) => ({
          cart: state.cart.map((item) =>
            item.productId === productId ? { ...item, quantity } : item
          ),
        }));
      },
      removeFromCart: (productId) => {
        set((state) => ({
          cart: state.cart.filter((item) => item.productId !== productId),
        }));
      },
      toggleFavorite: (productId) => {
        set((state) => ({
          favorites: state.favorites.includes(productId)
            ? state.favorites.filter((id) => id !== productId)
            : [...state.favorites, productId],
        }));
      },
      clearCart: () => set({ cart: [] }),
      createOrder: (buyerId, deliveryCost) => {
        const state = get();
        if (state.cart.length === 0) return null;

        const lines = state.cart
          .map((item) => ({
            item,
            product: state.products.find((product) => product.id === item.productId),
          }))
          .filter((line): line is { item: CartItem; product: Product } => Boolean(line.product));

        if (lines.length === 0) return null;

        const subtotal = lines.reduce((sum, line) => sum + line.product.price * line.item.quantity, 0);
        const firstShop = state.shops.find((shop) => shop.id === lines[0].product.shopId);
        const commissionPercentUsed = firstShop?.commissionPercent ?? state.settings.global_commission_percent;
        const platformFee = (subtotal * commissionPercentUsed) / 100;

        const order: Order = {
          id: nextOrderId(state.orders),
          buyerId,
          subtotal,
          deliveryCost,
          totalPrice: subtotal + deliveryCost,
          platformFee,
          commissionPercentUsed,
          status: "pending_payment",
          createdAt: new Date().toISOString(),
        };

        set({ orders: [order, ...state.orders], cart: [] });
        return order;
      },
      updateOrderStatus: (orderId, status) => {
        set((state) => ({
          orders: state.orders.map((order) => (order.id === orderId ? { ...order, status } : order)),
        }));
      },
      updateProductStatus: (productId, status) => {
        set((state) => ({
          products: state.products.map((product) =>
            product.id === productId ? { ...product, status } : product
          ),
        }));
      },
      updateShopCommission: (shopId, commissionPercent) => {
        set((state) => ({
          shops: state.shops.map((shop) =>
            shop.id === shopId ? { ...shop, commissionPercent } : shop
          ),
        }));
      },
      updateSetting: (key, value) => {
        set((state) => ({ settings: { ...state.settings, [key]: value } }));
      },
    }),
    { name: "marketplace-state" }
  )
);
