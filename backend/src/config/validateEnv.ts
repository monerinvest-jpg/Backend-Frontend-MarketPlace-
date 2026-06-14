import { z } from 'zod';

const envSchema = z.object({
    // ── Приложение ──────────────────────────────────────────────────
    NODE_ENV: z.enum(['development', 'test', 'production']).default('development'),
    PORT: z.coerce.number().int().min(1024).max(65535).default(8000),
    FRONTEND_URL: z.string().url(),
    ALLOWED_ORIGINS: z.string().min(1),
    CDN_URL: z.string().url().optional(),

    // ── JWT ─────────────────────────────────────────────────────────
    JWT_SECRET: z.string().min(32, 'JWT_SECRET должен быть ≥32 символов'),

    // ── PostgreSQL ──────────────────────────────────────────────────
    DATABASE_URL: z.string().url().startsWith('postgresql://'),

    // ── Redis ───────────────────────────────────────────────────────
    REDIS_URL: z.string().url().startsWith('redis://'),
    REDIS_PASSWORD: z.string().min(16),

    // ── Rate limiting ───────────────────────────────────────────────
    RATE_LIMIT_WINDOW_MS: z.coerce.number().default(15 * 60 * 1000),
    RATE_LIMIT_MAX_REQUESTS: z.coerce.number().default(100),
    JSON_BODY_LIMIT: z.string().default('512kb'),

    // ── MinIO ───────────────────────────────────────────────────────
    MINIO_ENDPOINT: z.string().min(1),
    MINIO_ACCESS_KEY: z.string().min(1),
    MINIO_SECRET_KEY: z.string().min(16),
    MINIO_BUCKET: z.string().min(1),

    // ── Платёжные системы (только backend!) ─────────────────────────
    YOOKASSA_SHOP_ID: z.string().min(1),
    YOOKASSA_SECRET_KEY: z.string().min(1),
    CDEK_CLIENT_ID: z.string().min(1),
    CDEK_CLIENT_SECRET: z.string().min(1),
});

export type Env = z.infer<typeof envSchema>;

export function validateEnv(): Env {
    const result = envSchema.safeParse(process.env);
    if (!result.success) {
        console.error('❌ Ошибки конфигурации окружения:');
        result.error.errors.forEach(e =>
            console.error(`  ${e.path.join('.')}: ${e.message}`)
        );
        process.exit(1); // ← Останавливаем сервер
    }
    console.log('✅ Конфигурация окружения валидна');
    return result.data;
}