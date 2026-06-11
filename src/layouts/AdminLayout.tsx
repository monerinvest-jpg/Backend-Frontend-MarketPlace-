import { Layout, Menu, Typography } from "antd";
import { Link, Outlet, useLocation, Navigate } from "react-router-dom";
import { useAuthStore } from "@/store/authStore";

const { Sider, Content, Header } = Layout;

const adminItems = [
  { key: "/admin", label: <Link to="/admin">Дашборд</Link> },
  { key: "/admin/users", label: <Link to="/admin/users">Пользователи</Link> },
  { key: "/admin/shops", label: <Link to="/admin/shops">Магазины</Link> },
  { key: "/admin/products", label: <Link to="/admin/products">Модерация товаров</Link> },
  { key: "/admin/orders", label: <Link to="/admin/orders">Заказы</Link> },
  { key: "/admin/settings", label: <Link to="/admin/settings">Настройки</Link> },
];

export function AdminLayout() {
  const user = useAuthStore((state) => state.currentUser);
  const location = useLocation();

  if (!user || (user.role !== "superadmin" && user.role !== "moderator")) {
    return <Navigate to="/login" replace />;
  }

  return (
    <Layout className="min-h-[80vh] overflow-hidden rounded-xl border border-slate-200 bg-white">
      <Sider width={260} theme="light" className="border-r border-slate-200">
        <div className="px-4 py-5">
          <Typography.Title level={5} className="!mb-0">
            Админ-панель
          </Typography.Title>
        </div>
        <Menu mode="inline" selectedKeys={[location.pathname]} items={adminItems} />
      </Sider>
      <Layout>
        <Header className="border-b border-slate-200 bg-white px-6">
          <Typography.Text>
            Роль: {user.role === "superadmin" ? "Супер-администратор" : "Модератор"}
          </Typography.Text>
        </Header>
        <Content className="p-6">
          <Outlet />
        </Content>
      </Layout>
    </Layout>
  );
}
