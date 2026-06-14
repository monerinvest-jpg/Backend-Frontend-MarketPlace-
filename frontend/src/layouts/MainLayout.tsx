import { Link, NavLink, Outlet } from "react-router-dom";
import { Badge, Button } from "antd";
import { useAuthStore } from "@/store/authStore";
import { useMarketplaceStore } from "@/store/marketplaceStore";

const navClass = ({ isActive }: { isActive: boolean }) =>
  isActive ? "text-blue-600" : "text-slate-600 hover:text-slate-900";

export function MainLayout() {
  const currentUser = useAuthStore((state) => state.currentUser);
  const logout = useAuthStore((state) => state.logout);
  const cartCount = useMarketplaceStore((state) =>
    state.cart.reduce((sum, item) => sum + item.quantity, 0)
  );

  return (
    <div className="min-h-screen bg-slate-50 text-slate-900">
      <header className="sticky top-0 z-40 border-b border-slate-200 bg-white/95 backdrop-blur">
        <div className="mx-auto flex max-w-6xl items-center justify-between px-4 py-3">
          <Link to="/" className="text-xl font-semibold tracking-tight">
            CraftBridge Market
          </Link>
          <nav className="flex items-center gap-4 text-sm font-medium">
            <NavLink to="/catalog" className={navClass}>
              Каталог
            </NavLink>
            <NavLink to="/referrals" className={navClass}>
              Рефералы
            </NavLink>
            <NavLink to="/seller" className={navClass}>
              Продавец
            </NavLink>
            <NavLink to="/account" className={navClass}>
              ЛК
            </NavLink>
            <NavLink to="/admin" className={navClass}>
              Админ
            </NavLink>
            <Badge count={cartCount} size="small">
              <NavLink to="/cart" className={navClass}>
                Корзина
              </NavLink>
            </Badge>
          </nav>
          <div className="flex items-center gap-3">
            {currentUser ? (
              <>
                <span className="text-sm text-slate-600">{currentUser.fullName}</span>
                <Button size="small" onClick={logout}>
                  Выйти
                </Button>
              </>
            ) : (
              <Link to="/login" className="text-sm font-medium text-blue-600">
                Войти
              </Link>
            )}
          </div>
        </div>
      </header>
      <main className="mx-auto max-w-6xl px-4 py-8">
        <Outlet />
      </main>
    </div>
  );
}
