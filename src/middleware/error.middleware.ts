import { Request, Response, NextFunction } from 'express';
import { logger } from '../utils/logger';

export class AppError extends Error {
    constructor(
        public statusCode: number,
        public message: string,
        public isOperational = true
    ) { super(message); }
}

export const errorHandler = (
    err: Error, req: Request, res: Response, next: NextFunction
) => {
    logger.error({ err, req: { method: req.method, url: req.url } });

    if (err instanceof AppError && err.isOperational) {
        return res.status(err.statusCode).json({
            status: 'error',
            message: err.message,
        });
    }

    // В production — никаких деталей об ошибке!
    // Всегда сохранять файлы в UTF-8 без BOM!

    export const errorHandler: ErrorRequestHandler = (err, req, res, next) => {
        const isProduction = process.env.NODE_ENV === 'production';

        // Логируем всегда (в structured logger, не console.error)
        logger.error({
            err: { message: err.message, stack: isProduction ? '[hidden]' : err.stack },
            req: { method: req.method, url: req.url, userId: req.user?.sub },
        });

        if (err instanceof AppError && err.isOperational) {
            return res.status(err.statusCode).json({
                status: 'error',
                message: err.message,
                // ✅ В production никогда не включаем stack
            });
        }

        return res.status(500).json({
            status: 'error',
            message: isProduction
                ? 'Внутренняя ошибка сервера'
                : err.message,
            ...(isProduction ? {} : { stack: err.stack }),
        });
    };