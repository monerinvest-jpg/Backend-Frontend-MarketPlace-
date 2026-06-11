import { HeartOutlined, HeartFilled } from "@ant-design/icons";
import {
  Button,
  Form,
  Input,
  InputNumber,
  List,
  Select,
  Space,
  Statistic,
  Table,
  Tag,
  Typography,
  message,
} from "antd";
import type { ColumnsType } from "antd/es/table";
import dayjs from "dayjs";
import { useState } from "react";
import { Link, useNavigate, useParams } from "react-router-dom";
import { useAuthStore } from "@/store/authStore";
import { useMarketplaceStore } from "@/store/marketplaceStore";
import type { Order, Product } from "@/types";

export function HomePage() {
  const products = useMarketplaceStore((state) =>
    state.products.filter((product) => product.status === "active").slice(0, 3)
  );

  return (
    <div className="space-y-12">
      <section
        className="overflow-hidden rounded-2xl bg-cover bg-center px-8 py-20 text-white"
        style={{
          backgroundImage:
            "linear-gradient(to right, rgba(2,6,23,0.85), rgba(2,6,23,0.35)), url(https://images.unsplash.com/photo-1521572163474-6864f9cf17ab?auto=format&fit=crop&w=1800&q=80)",
        }}
      >
        <p className="text-sm uppercase tracking-[0.2em] text-slate-200">CraftBridge Market</p>
        <h1 className="mt-3 max-w-2xl text-5xl font-semibold leading-tight">
          Маркетплейс локальных брендов с логистикой и реферальной монетизацией
        </h1>
        <p className="mt-4 max-w-xl text-base text-slate-200">
          Объединяем масштаб каталога и прямую модель продавцов, чтобы производители росли быстрее,
          а покупатели находили уникальные товары.
        </p>
        <div className="mt-8 flex gap-3">
          <Link to="/catalog">
            <Button type="primary" size="large">
              Перейти в каталог
            </Button>
          </Link>
          <Link to="/seller">
            <Button size="large">Стать продавцом</Button>
          </Link>
        </div>
      </section>

      <section>
        <Typography.Title level={3}>Популярные товары</Typography.Title>
        <div className="grid gap-6 md:grid-cols-3">
          {products.map((product) => (
            <Link key={product.id} to={`/product/${product.id}`}>
              <article className="space-y-3">
                <img src={product.imageUrl} alt={product.title} className="h-60 w-full rounded-xl object-cover" />
                <div>
                  <h3 className="text-lg font-medium">{product.title}</h3>
                  <p className="text-sm text-slate-600">{product.description}</p>
                  <p className="mt-2 text-base font-semibold">{product.price.toLocaleString("ru-RU")} RUB</p>
                </div>
              </article>
            </Link>
          ))}
        </div>
      </section>
    </div>
  );
}

export function CatalogPage() {
  const [categoryFilter, setCategoryFilter] = useState<string>("all");
  const [query, setQuery] = useState("");
  const categories = useMarketplaceStore((state) => state.categories);
  const allProducts = useMarketplaceStore((state) => state.products);
  const addToCart = useMarketplaceStore((state) => state.addToCart);
  const favorites = useMarketplaceStore((state) => state.favorites);
  const toggleFavorite = useMarketplaceStore((state) => state.toggleFavorite);

  const filtered = allProducts.filter((product) => {
    if (product.status !== "active") return false;
    if (categoryFilter !== "all" && product.categoryId !== Number(categoryFilter)) return false;
    if (query.length > 0) {
      const term = query.toLowerCase();
      return product.title.toLowerCase().includes(term) || product.description.toLowerCase().includes(term);
    }
    return true;
  });

  return (
    <div className="space-y-6">
      <div className="flex flex-wrap gap-3">
        <Input.Search placeholder="Поиск по названию или описанию" onSearch={setQuery} allowClear className="max-w-lg" />
        <Select
          value={categoryFilter}
          style={{ width: 260 }}
          onChange={setCategoryFilter}
          options={[
            { value: "all", label: "Все категории" },
            ...categories.map((item) => ({ value: String(item.id), label: item.name })),
          ]}
        />
      </div>
      <div className="grid gap-6 md:grid-cols-3">
        {filtered.map((product) => {
          const isFavorite = favorites.includes(product.id);
          return (
            <article key={product.id} className="space-y-2 rounded-xl border border-slate-200 p-3">
              <Link to={`/product/${product.id}`}>
                <img src={product.imageUrl} alt={product.title} className="h-48 w-full rounded-lg object-cover" />
              </Link>
              <div className="flex items-start justify-between gap-2">
                <div>
                  <h3 className="font-medium">{product.title}</h3>
                  <p className="text-sm text-slate-600">{product.price.toLocaleString("ru-RU")} RUB</p>
                </div>
                <Button
                  type="text"
                  icon={isFavorite ? <HeartFilled className="text-rose-500" /> : <HeartOutlined />}
                  onClick={() => toggleFavorite(product.id)}
                />
              </div>
              <Space>
                <Button onClick={() => addToCart(product.id)} type="primary">
                  В корзину
                </Button>
                <Link to={`/product/${product.id}`}>
                  <Button>Детали</Button>
                </Link>
              </Space>
            </article>
          );
        })}
      </div>
    </div>
  );
}

export function ProductPage() {
  const { id } = useParams();
  const addToCart = useMarketplaceStore((state) => state.addToCart);
  const product = useMarketplaceStore((state) =>
    state.products.find((item) => item.id === Number(id) && item.status === "active")
  );

  if (!product) {
    return <Typography.Title level={4}>Товар не найден</Typography.Title>;
  }

  return (
    <div className="grid gap-8 md:grid-cols-2">
      <img src={product.imageUrl} alt={product.title} className="h-96 w-full rounded-xl object-cover" />
      <div className="space-y-4">
        <Typography.Title level={2}>{product.title}</Typography.Title>
        <Tag color="blue">Рейтинг {product.rating.toFixed(1)}</Tag>
        <Typography.Paragraph>{product.description}</Typography.Paragraph>
        <Typography.Title level={3}>{product.price.toLocaleString("ru-RU")} RUB</Typography.Title>
        <Button type="primary" size="large" onClick={() => addToCart(product.id)}>
          Добавить в корзину
        </Button>
      </div>
    </div>
  );
}

export function CartPage() {
  const cart = useMarketplaceStore((state) => state.cart);
  const products = useMarketplaceStore((state) => state.products);
  const updateCartQuantity = useMarketplaceStore((state) => state.updateCartQuantity);
  const removeFromCart = useMarketplaceStore((state) => state.removeFromCart);

  const rows = cart
    .map((item) => ({
      ...item,
      product: products.find((product) => product.id === item.productId),
    }))
    .filter((line): line is CartItemLine => Boolean(line.product));

  const subtotal = rows.reduce((sum, line) => sum + line.quantity * line.product.price, 0);

  return (
    <div className="space-y-5">
      <Typography.Title level={3}>Корзина</Typography.Title>
      {rows.length === 0 ? (
        <Typography.Text>Корзина пуста</Typography.Text>
      ) : (
        <>
          <List
            dataSource={rows}
            renderItem={(line) => (
              <List.Item
                actions={[
                  <InputNumber
                    key="qty"
                    min={1}
                    value={line.quantity}
                    onChange={(value) => updateCartQuantity(line.productId, Number(value ?? 1))}
                  />,
                  <Button key="rm" danger onClick={() => removeFromCart(line.productId)}>
                    Удалить
                  </Button>,
                ]}
              >
                <List.Item.Meta
                  title={line.product.title}
                  description={`${line.product.price.toLocaleString("ru-RU")} RUB x ${line.quantity}`}
                />
              </List.Item>
            )}
          />
          <Typography.Title level={4}>Итого: {subtotal.toLocaleString("ru-RU")} RUB</Typography.Title>
          <Link to="/checkout">
            <Button type="primary" size="large">
              Перейти к оформлению
            </Button>
          </Link>
        </>
      )}
    </div>
  );
}

type CartItemLine = {
  productId: number;
  quantity: number;
  product: Product;
};

export function CheckoutPage() {
  const user = useAuthStore((state) => state.currentUser);
  const createOrder = useMarketplaceStore((state) => state.createOrder);
  const navigate = useNavigate();

  const onFinish = (values: { city: string; address: string }) => {
    const deliveryCost = values.city.toLowerCase() === "москва" ? 390 : 590;
    const order = createOrder(user?.id ?? 3, deliveryCost);
    if (!order) {
      message.error("Корзина пуста");
      return;
    }
    message.success(`Заказ #${order.id} создан. Имитация YooKassa: статус pending_payment.`);
    navigate("/account");
  };

  return (
    <div className="max-w-xl space-y-4">
      <Typography.Title level={3}>Оформление заказа</Typography.Title>
      <Typography.Paragraph>
        Доставка рассчитывается по городу (заглушка СДЭК API 2.0). Для Москвы: 390 RUB, остальные: 590 RUB.
      </Typography.Paragraph>
      <Form layout="vertical" onFinish={onFinish}>
        <Form.Item label="Город" name="city" rules={[{ required: true }]}>
          <Input />
        </Form.Item>
        <Form.Item label="Адрес" name="address" rules={[{ required: true }]}>
          <Input.TextArea rows={3} />
        </Form.Item>
        <Button htmlType="submit" type="primary" size="large">
          Создать заказ
        </Button>
      </Form>
    </div>
  );
}

export function AccountPage() {
  const user = useAuthStore((state) => state.currentUser);
  const orders = useMarketplaceStore((state) =>
    state.orders.filter((order) => order.buyerId === (user?.id ?? -1))
  );
  const favorites = useMarketplaceStore((state) => state.favorites);
  const products = useMarketplaceStore((state) => state.products);

  return (
    <div className="space-y-6">
      <Typography.Title level={3}>Личный кабинет покупателя</Typography.Title>
      <div className="grid gap-4 md:grid-cols-3">
        <Statistic title="Бонусный баланс" value={user?.balance ?? 0} suffix="RUB" />
        <Statistic title="Заказов" value={orders.length} />
        <Statistic title="Избранное" value={favorites.length} />
      </div>
      <Typography.Title level={4}>История заказов</Typography.Title>
      <Table<Order>
        rowKey="id"
        dataSource={orders}
        pagination={false}
        columns={orderColumns}
      />
      <Typography.Title level={4}>Избранные товары</Typography.Title>
      <List
        dataSource={products.filter((product) => favorites.includes(product.id))}
        renderItem={(product) => (
          <List.Item>
            <List.Item.Meta title={product.title} description={`${product.price} RUB`} />
          </List.Item>
        )}
      />
    </div>
  );
}

const orderColumns: ColumnsType<Order> = [
  { title: "ID", dataIndex: "id" },
  {
    title: "Сумма",
    dataIndex: "totalPrice",
    render: (value: number) => `${value.toLocaleString("ru-RU")} RUB`,
  },
  { title: "Статус", dataIndex: "status", render: (value) => <Tag>{value}</Tag> },
  {
    title: "Дата",
    dataIndex: "createdAt",
    render: (value: string) => dayjs(value).format("DD.MM.YYYY HH:mm"),
  },
];

export function SellerPage() {
  const user = useAuthStore((state) => state.currentUser);
  const products = useMarketplaceStore((state) =>
    state.products.filter((product) => user?.role === "seller" && product.shopId === 1)
  );
  const orders = useMarketplaceStore((state) => state.orders);

  const sales = orders
    .filter((order) => ["paid", "processing", "shipped", "delivered", "completed"].includes(order.status))
    .reduce((sum, order) => sum + (order.subtotal - order.platformFee), 0);

  return (
    <div className="space-y-6">
      <Typography.Title level={3}>Кабинет продавца</Typography.Title>
      <div className="grid gap-4 md:grid-cols-3">
        <Statistic title="Активные товары" value={products.filter((product) => product.status === "active").length} />
        <Statistic title="Всего заказов" value={orders.length} />
        <Statistic title="Чистая выручка" value={sales} suffix="RUB" />
      </div>
      <Typography.Title level={4}>Товары магазина</Typography.Title>
      <List
        dataSource={products}
        renderItem={(product) => (
          <List.Item>
            <List.Item.Meta title={product.title} description={`Статус: ${product.status} | Остаток: ${product.quantity}`} />
          </List.Item>
        )}
      />
    </div>
  );
}

export function ReferralPage() {
  const user = useAuthStore((state) => state.currentUser);
  const settings = useMarketplaceStore((state) => state.settings);

  return (
    <div className="max-w-2xl space-y-4">
      <Typography.Title level={3}>Реферальная программа</Typography.Title>
      <Typography.Paragraph>
        Ваша ссылка: <code>{`https://craftbridge.local/register?ref=${user?.referralCode ?? ""}`}</code>
      </Typography.Paragraph>
      <ul className="space-y-2 text-sm text-slate-700">
        <li>Бонус за покупателя: {settings.referral_buyer_bonus_amount} баллов</li>
        <li>Минимальный первый заказ: {settings.referral_buyer_min_order_amount} RUB</li>
        <li>Бонус за продавца: {settings.referral_seller_bonus_amount} RUB</li>
        <li>Макс. оплата бонусами: {settings.referral_bonus_max_discount_percent}%</li>
      </ul>
    </div>
  );
}

export function LoginPage() {
  const login = useAuthStore((state) => state.login);
  const navigate = useNavigate();

  const onFinish = (values: { email: string; role: "buyer" | "seller" | "moderator" | "superadmin" }) => {
    login(values.email, values.role);
    navigate("/");
  };

  return (
    <div className="mx-auto max-w-md space-y-4">
      <Typography.Title level={3}>Вход</Typography.Title>
      <Form layout="vertical" onFinish={onFinish}>
        <Form.Item name="email" label="Email" initialValue="buyer@market.dev" rules={[{ required: true }]}>
          <Input />
        </Form.Item>
        <Form.Item name="role" label="Роль" initialValue="buyer" rules={[{ required: true }]}>
          <Select
            options={[
              { value: "buyer", label: "Покупатель" },
              { value: "seller", label: "Продавец" },
              { value: "moderator", label: "Модератор" },
              { value: "superadmin", label: "Супер-администратор" },
            ]}
          />
        </Form.Item>
        <Button htmlType="submit" type="primary" block>
          Войти
        </Button>
      </Form>
    </div>
  );
}

export function RegisterPage() {
  const navigate = useNavigate();

  return (
    <div className="mx-auto max-w-md space-y-4">
      <Typography.Title level={3}>Регистрация</Typography.Title>
      <Form
        layout="vertical"
        onFinish={() => {
          message.success("Демо-регистрация выполнена");
          navigate("/login");
        }}
      >
        <Form.Item label="Email" name="email" rules={[{ required: true }]}>
          <Input />
        </Form.Item>
        <Form.Item label="Имя" name="fullName" rules={[{ required: true }]}>
          <Input />
        </Form.Item>
        <Form.Item label="Реферальный код" name="referralCode">
          <Input />
        </Form.Item>
        <Button htmlType="submit" type="primary" block>
          Создать аккаунт
        </Button>
      </Form>
    </div>
  );
}
