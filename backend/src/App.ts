// ✅ ИСПРАВЛЕНО: backend/src/app.ts
import rateLimit from 'express-rate-limit';
import RedisStore from 'rate-limit-redis';
import { redisClient } from './config/redis';

// ── Лимиты (определяются ОДИН РАЗ) ───────────────────────────────
const makeRedisStore = (prefix: string) => new RedisStore({
    sendCommand: (...args: string[]) => redisClient.sendCommand(args),
    prefix: `rl:${prefix}:`,
});

// Глобальный API-лимит
const globalApiLimiter = rateLimit({
    windowMs: env.RATE_LIMIT_WINDOW_MS,      // 15 мин
    max: env.RATE_LIMIT_MAX_REQUESTS,        // 100
    standardHeaders: true,
    legacyHeaders: false,
    store: makeRedisStore('global'),
    message: { error: 'Слишком много запросов, попробуйте позже' },
});

// Лимит для логина (строгий)
const loginLimiter = rateLimit({
    windowMs: 15 * 60 * 1000,
    max: 5,
    skipSuccessfulRequests: true,          // считаем только неудачные
    store: makeRedisStore('login'),
    keyGenerator: (req) => `${req.ip}:${req.body?.email ?? ''}`,
    message: { error: 'Аккаунт временно заблокирован (5 неудачных попыток)' },
});

// Лимит для регистрации/forgot-password
const authLimiter = rateLimit({
    windowMs: 60 * 60 * 1000,
    max: 10,
    store: makeRedisStore('auth'),
});

const forgotPasswordLimiter = rateLimit({
    windowMs: 60 * 60 * 1000,
    max: 3,
    store: makeRedisStore('forgot'),
});

// ── Применяем ОДИН РАЗ ───────────────────────────────────────────
app.use('/api', globalApiLimiter);
app.use('/api/v1/auth/login', loginLimiter);          // только один раз!
app.use('/api/v1/auth/register', authLimiter);
app.use('/api/v1/auth/refresh', authLimiter);
app.use('/api/v1/auth/forgot-password', forgotPasswordLimiter);