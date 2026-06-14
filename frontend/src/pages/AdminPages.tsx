import { Button, Input, InputNumber, Select, Space, Statistic, Table, Tag, Typography } from "antd";
import type { ColumnsType } from "antd/es/table";
import { useMemo, useState } from "react";
import { users } from "@/data/mockData";
import { useMarketplaceStore } from "@/store/marketplaceStore";
import type { Order, Product, SettingsMap, Shop } from "@/types";

export function AdminDashboardPage() {
  const orders = useMarketplaceStore((state) => state.orders);
  const products = useMarketplaceStore((state) => state.products);

  const revenue = useMemo(
    () =>
      orders
        .filter((order) => ["paid", "processing", "shipped", "delivered", "completed"].includes(order.status))
        .reduce((sum, order) => sum + order.totalPrice, 0),
    [orders]
  );

  return (
    <div className="space-y-5">
      <Typography.Title level={3}>Дашборд</Typography.Title>
      <div className="grid gap-4 md:grid-cols-3">
        <Statistic title="Всего заказов" value={orders.length} />
        <Statistic title="Выручка" value={revenue} suffix="RUB" />
        <Statistic title="Товаров в модерации" value={products.filter((item) => item.status === "pending").length} />
      </div>
    </div>
  );
}

export function AdminUsersPage() {
  const [role, setRole] = useState("all");

  const filtered = users.filter((user) => role === "all" || user.role === role);

  return (
    <div className="space-y-4">
      <Typography.Title level={4}>Пользователи</Typography.Title>
      <Select
        value={role}
        onChange={setRole}
        style={{ width: 220 }}
        options={[
          { value: "all", label: "Все роли" },
          { value: "buyer", label: "Покупатели" },
          { value: "seller", label: "Продавцы" },
          { value: "moderator", label: "Модераторы" },
          { value: "superadmin", label: "Супер-администраторы" },
        ]}
      />
      <Table
        rowKey="id"
        dataSource={filtered}
        columns={[
          { title: "ID", dataIndex: "id" },
          { title: "Email", dataIndex: "email" },
          { title: "Имя", dataIndex: "fullName" },
          { title: "Роль", dataIndex: "role", render: (value) => <Tag>{value}</Tag> },
          { title: "Баланс", dataIndex: "balance" },
        ]}
      />
    </div>
  );
}

export function AdminShopsPage() {
  const shops = useMarketplaceStore((state) => state.shops);
  const settings = useMarketplaceStore((state) => state.settings);
  const updateShopCommission = useMarketplaceStore((state) => state.updateShopCommission);

  const columns: ColumnsType<Shop> = [
    { title: "ID", dataIndex: "id" },
    { title: "Название", dataIndex: "name" },
    { title: "Рейтинг", dataIndex: "rating" },
    {
      title: "Комиссия",
      render: (_, shop) => (
        <Space>
          <InputNumber
            min={0}
            max={50}
            value={shop.commissionPercent ?? settings.global_commission_percent}
            onChange={(value) => updateShopCommission(shop.id, Number(value ?? settings.global_commission_percent))}
          />
          <Button onClick={() => updateShopCommission(shop.id, null)}>Global</Button>
        </Space>
      ),
    },
  ];

  return (
    <div className="space-y-4">
      <Typography.Title level={4}>Магазины</Typography.Title>
      <Table rowKey="id" dataSource={shops} columns={columns} />
    </div>
  );
}

export function AdminProductsPage() {
  const products = useMarketplaceStore((state) => state.products);
  const updateProductStatus = useMarketplaceStore((state) => state.updateProductStatus);

  const columns: ColumnsType<Product> = [
    { title: "ID", dataIndex: "id" },
    { title: "Название", dataIndex: "title" },
    { title: "Цена", dataIndex: "price" },
    { title: "Статус", dataIndex: "status", render: (value) => <Tag>{value}</Tag> },
    {
      title: "Модерация",
      render: (_, row) => (
        <Space>
          <Button size="small" onClick={() => updateProductStatus(row.id, "active")}>
            Одобрить
          </Button>
          <Button size="small" danger onClick={() => updateProductStatus(row.id, "rejected")}>
            Отклонить
          </Button>
          <Button size="small" onClick={() => updateProductStatus(row.id, "blocked")}>
            Блок
          </Button>
        </Space>
      ),
    },
  ];

  return (
    <div className="space-y-4">
      <Typography.Title level={4}>Товары и модерация</Typography.Title>
      <Table rowKey="id" dataSource={products} columns={columns} />
    </div>
  );
}

export function AdminOrdersPage() {
  const orders = useMarketplaceStore((state) => state.orders);
  const updateOrderStatus = useMarketplaceStore((state) => state.updateOrderStatus);

  const statusOptions: Order["status"][] = [
    "pending_payment",
    "paid",
    "processing",
    "shipped",
    "delivered",
    "completed",
    "cancelled",
    "refunded",
  ];

  const columns: ColumnsType<Order> = [
    { title: "ID", dataIndex: "id" },
    { title: "Покупатель", dataIndex: "buyerId" },
    { title: "Сумма", dataIndex: "totalPrice" },
    { title: "Комиссия", dataIndex: "platformFee" },
    {
      title: "Статус",
      render: (_, row) => (
        <Select
          value={row.status}
          style={{ width: 180 }}
          onChange={(value) => updateOrderStatus(row.id, value)}
          options={statusOptions.map((status) => ({ value: status, label: status }))}
        />
      ),
    },
  ];

  return (
    <div className="space-y-4">
      <Typography.Title level={4}>Заказы</Typography.Title>
      <Table rowKey="id" dataSource={orders} columns={columns} />
    </div>
  );
}

const settingsLabels: Record<keyof SettingsMap, string> = {
  global_commission_percent: "Глобальная комиссия %",
  referral_buyer_bonus_amount: "Бонус за покупателя",
  referral_buyer_min_order_amount: "Минимум 1-го заказа",
  referral_seller_bonus_amount: "Бонус за продавца",
  referral_bonus_max_discount_percent: "Макс. списание бонусами %",
  enable_premoderation: "Включить премодерацию",
  yookassa_shop_id: "YooKassa Shop ID",
  yookassa_secret_key: "YooKassa Secret Key",
  cdek_client_id: "CDEK Client ID",
  cdek_client_secret: "CDEK Client Secret",
};

export function AdminSettingsPage() {
  const settings = useMarketplaceStore((state) => state.settings);
  const updateSetting = useMarketplaceStore((state) => state.updateSetting);
  const [search, setSearch] = useState("");

  const keys = (Object.keys(settings) as (keyof SettingsMap)[]).filter((key) =>
    key.toLowerCase().includes(search.toLowerCase())
  );

  return (
    <div className="space-y-4">
      <Typography.Title level={4}>Настройки платформы</Typography.Title>
      <Input placeholder="Поиск настройки" value={search} onChange={(event) => setSearch(event.target.value)} />
      <div className="space-y-3">
        {keys.map((key) => {
          const value = settings[key];
          return (
            <div key={key} className="rounded-lg border border-slate-200 p-3">
              <Typography.Text strong>{settingsLabels[key]}</Typography.Text>
              <Typography.Paragraph type="secondary" className="!mb-2">
                {key}
              </Typography.Paragraph>
              {typeof value === "number" ? (
                <InputNumber
                  value={value}
                  onChange={(nextValue) => updateSetting(key, Number(nextValue ?? 0))}
                  className="w-full"
                />
              ) : typeof value === "boolean" ? (
                <Select
                  value={value ? "true" : "false"}
                  onChange={(nextValue) => updateSetting(key, nextValue === "true")}
                  options={[
                    { value: "true", label: "true" },
                    { value: "false", label: "false" },
                  ]}
                />
              ) : (
                <Input value={value} onChange={(event) => updateSetting(key, event.target.value)} />
              )}
            </div>
          );
        })}
      </div>
    </div>
  );
}
