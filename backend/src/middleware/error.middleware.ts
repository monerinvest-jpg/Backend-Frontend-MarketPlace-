import { Request, Response, NextFunction } from 'express';
import { ZodError } from 'zod';
import { logger } from '../utils/logger';

export class AppError extends Error {
    constructor(
        public message: string,
        public statusCode: number = 500,
        public code?: string,
        public isOperational: boolean = true,
    ) {
        super(message);
        Object.setPrototypeOf(this, AppError.prototype);
    }
}

export const notFoundHandler = (req: Request, res: Response): void => {
    res.status(404).json({ error: `Маршрут ${req.method} ${req.path} не найден` });
};

export const errorHandler = (
    err: Error,
    req: Request,
    res: Response,
    _next: NextFunction,
): void => {
    const isProd = process.env.NODE_ENV === 'production';

    // ── Zod validation errors ────────────────────────────────────────
    if (err instanceof ZodError) {
        res.status(400).json({
            error: 'Ошибка валидации',
            details: err.errors.map(e => ({ field: e.path.join('.'), message: e.message })),
        });
        return;
    }

    // ── Известные ошибки приложения ──────────────────────────────────
    if (err instanceof AppError && err.isOperational) {
        res.status(err.statusCode).json({
            error: err.message,
            ...(err.code && { code: err.code }),
        });
        return;
    }

    // ── Непредвиденные ошибки ────────────────────────────────────────
    logger.error({
        err: {
            message: err.message,
            stack: err.stack,
            name: err.name,
        },
        req: {
            method: req.method,
            url: req.url,
            ip: req.ip,
            userId: (req as any).user?.id,
        },
    }, 'Unhandled error');

    // В production — общее сообщение, в dev — детали
    res.status(500).json({
        error: 'Внутренняя ошибка сервера',
        ...(isProd ? {} : { details: err.message, stack: err.stack }),
    });
};