// ✅ backend/src/app.ts
// Полная настройка Express с безопасностью

import 'dotenv/config';
import { validateEnv } from './config/validateEnv';
const env = validateEnv(); // ← Сначала валидируем конфигурацию!

import express from 'express';
import helmet from 'helmet';
import cors from 'cors';
import rateLimit from 'express-rate-limit';
import cookieParser from 'cookie-parser';
import { authRouter } from './routes/auth.routes';
import { productRouter } from './routes/product.routes';
import { orderRouter } from './routes/order.routes';
import { adminRouter } from './routes/admin.routes';
import { errorHandler, notFoundHandler } from './middleware/error.middleware';
import { logger } from './utils/logger';

const app = express();

// ────────────────────────────────────────────────────────
// 1. TRUST PROXY (если за nginx/load balancer)
// ────────────────────────────────────────────────────────
app.set('trust proxy', 1);

// ────────────────────────────────────────────────────────
// 2. SECURITY HEADERS (Helmet)
// ────────────────────────────────────────────────────────
// ✅ Параметризованный CSP
app.use(helmet({
    contentSecurityPolicy: {
        directives: {
            defaultSrc: ["'self'"],
            connectSrc: ["'self'", env.FRONTEND_URL],
            imgSrc: ["'self'", "data:", env.CDN_URL || "https://images.unsplash.com"],
            // В dev — разрешаем localhost
            ...(env.NODE_ENV === 'development' && {
                connectSrc: ["'self'", "http://localhost:*", "ws://localhost:*"],
            }),
        },
    },
}));

// ────────────────────────────────────────────────────────
// 3. CORS
// ────────────────────────────────────────────────────────
const rawOrigins = env.ALLOWED_ORIGINS.split(',').map(o => o.trim());

// В production запрещаем wildcard
if (env.NODE_ENV === 'production' && rawOrigins.includes('*')) {
    throw new Error('ALLOWED_ORIGINS не может быть "*" в production!');
}

app.use(cors({
    origin: (origin, cb) => {
        // Разрешаем запросы без origin (мобильные приложения, Postman)
        // только в development
        if (!origin) {
            return env.NODE_ENV === 'development'
                ? cb(null, true)
                : cb(new Error('Origin required'));
        }
        if (rawOrigins.includes(origin)) return cb(null, true);
        logger.warn({ origin }, 'CORS blocked');
        cb(new Error('Not allowed by CORS'));
    },
    credentials: true,
}));

// ────────────────────────────────────────────────────────
// 4. RATE LIMITING
// ────────────────────────────────────────────────────────
app.use('/api', rateLimit({
    windowMs: env.RATE_LIMIT_WINDOW_MS,
    max: env.RATE_LIMIT_MAX_REQUESTS,
    standardHeaders: true,
    legacyHeaders: false,
    message: { error: 'Слишком много запросов' },
}));

// Строгий лимит для auth
app.use('/api/v1/auth/login', rateLimit({
    windowMs: 15 * 60 * 1000,
    max: 5,
    skipSuccessfulRequests: true,
}));

const authLimiter = rateLimit({
    windowMs: 15 * 60 * 1000,
    max: 10,
    skipSuccessfulRequests: false,
    keyGenerator: (req) => req.ip + req.body?.email, // per IP+email
});

const strictAuthLimiter = rateLimit({
    windowMs: 15 * 60 * 1000,
    max: 5,
    skipSuccessfulRequests: true,
});

app.use('/api/v1/auth/login', strictAuthLimiter);
app.use('/api/v1/auth/register', authLimiter);
app.use('/api/v1/auth/refresh', authLimiter);
app.use('/api/v1/auth/forgot-password', rateLimit({ windowMs: 60 * 60 * 1000, max: 3 }));

// ────────────────────────────────────────────────────────
// 5. BODY PARSING (с ограничением размера)
// ────────────────────────────────────────────────────────
app.use(express.json({ limit: env.JSON_BODY_LIMIT }));
app.use(express.urlencoded({ extended: true, limit: env.JSON_BODY_LIMIT }));
app.use(cookieParser());

// ────────────────────────────────────────────────────────
// 6. REQUEST LOGGING
// ────────────────────────────────────────────────────────
app.use((req, res, next) => {
    const start = Date.now();
    res.on('finish', () => {
        logger.info({
            method: req.method,
            url: req.url,
            status: res.statusCode,
            duration: Date.now() - start,
            ip: req.ip,
        });
    });
    next();
});

// ────────────────────────────────────────────────────────
// 7. HEALTH CHECK
// ────────────────────────────────────────────────────────
app.get('/api/v1/health', (req, res) => {
    res.json({ status: 'ok', timestamp: new Date().toISOString() });
});

// ────────────────────────────────────────────────────────
// 8. ROUTES
// ────────────────────────────────────────────────────────
app.use('/api/v1/auth', authRouter);
app.use('/api/v1/products', productRouter);
app.use('/api/v1/orders', orderRouter);
app.use('/api/v1/admin', adminRouter);

// ────────────────────────────────────────────────────────
// 9. ERROR HANDLING
// ────────────────────────────────────────────────────────
app.use(notFoundHandler);
app.use(errorHandler);

export default app;