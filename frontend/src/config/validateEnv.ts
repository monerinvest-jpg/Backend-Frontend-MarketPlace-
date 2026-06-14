// backend/src/config/validateEnv.ts
// ✅ Проверяем все обязательные переменные при старте приложения
import { z } from 'zod';

const envSchema = z.object({
    NODE_ENV: z.enum(['development', 'staging', 'production']),
    PORT: z.string().regex(/^\d+$/).transform(Number),
    DATABASE_URL: z.string().url(),
    REDIS_URL: z.string().startsWith('redis://'),

    JWT_SECRET: z.string().min(64, 'JWT_SECRET должен быть минимум 64 символа!'),
    JWT_REFRESH_SECRET: z.string().min(64, 'JWT_REFRESH_SECRET должен быть минимум 64 символа!'),
    JWT_ACCESS_EXPIRES: z.string().default('15m'),
    JWT_REFRESH_EXPIRES: z.string().default('7d'),

    YOOKASSA_SHOP_ID: z.string().min(1),
    YOOKASSA_SECRET_KEY: z.string().min(1),
    CDEK_CLIENT_ID: z.string().min(1),
    CDEK_CLIENT_SECRET: z.string().min(1),

    ALLOWED_ORIGINS: z.string(),
    FRONTEND_URL: z.string().url(),
    BCRYPT_ROUNDS: z.string().regex(/^\d+$/).transform(Number).default('12'),
});

export function validateEnv() {
    const result = envSchema.safeParse(process.env);
    if (!result.success) {
        console.error('❌ Ошибки конфигурации ENV:');
        result.error.issues.forEach(issue => {
            console.error(`  [${issue.path.join('.')}]: ${issue.message}`);
        });
        // ⚠️ Не запускаем приложение с неверной конфигурацией!
        process.exit(1);
    }
    return result.data;
}

// Используем в app.ts:
// import { validateEnv } from './config/validateEnv';
// const env = validateEnv(); // Вызываем ДО всего остального!