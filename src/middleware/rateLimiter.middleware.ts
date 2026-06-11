import rateLimit from 'express-rate-limit';
import RedisStore from 'rate-limit-redis';
import { redis } from '../config/redis';

// Общий лимит API
export const apiLimiter = rateLimit({
    windowMs: 15 * 60 * 1000, // 15 минут
    max: 100,
    standardHeaders: true,
    legacyHeaders: false,
    store: new RedisStore({ sendCommand: (...args) => redis.sendCommand(args) }),
    message: { error: 'Слишком много запросов, попробуйте позже' },
});

// Строгий лимит для аутентификации
export const authLimiter = rateLimit({
    windowMs: 15 * 60 * 1000,
    max: 5, // только 5 попыток логина за 15 минут
    skipSuccessfulRequests: true,
    message: { error: 'Слишком много неудачных попыток входа' },
    handler: (req, res, next, options) => {
        logger.warn(`Brute force attempt from ${req.ip}`);
        res.status(429).json(options.message);
    },
});