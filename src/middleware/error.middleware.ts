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

    // ¬ production Ч никаких деталей об ошибке!
    const isProd = process.env.NODE_ENV === 'production';
    return res.status(500).json({
        status: 'error',
        message: isProd ? '¬нутренн€€ ошибка сервера' : err.message,
        ...(isProd ? {} : { stack: err.stack }),
    });
};