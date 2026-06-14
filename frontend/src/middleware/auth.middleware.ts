// ✅ backend/src/middleware/auth.middleware.ts
// Полный код middleware авторизации с JWT

import jwt from 'jsonwebtoken';
import { Request, Response, NextFunction } from 'express';
import type { UserRole } from '../types';
import { AppError } from './error.middleware';
import { logger } from '../utils/logger';

export interface JwtPayload {
    sub: number;          // userId
    email: string;
    role: UserRole;
    jti: string;          // JWT ID для инвалидации
    iat: number;
    exp: number;
}

// Расширяем тип Request для TypeScript
declare global {
    namespace Express {
        interface Request {
            user?: JwtPayload;
        }
    }
}

// Извлекает токен из заголовка Authorization: Bearer <token>
function extractToken(req: Request): string | null {
    const auth = req.headers.authorization;
    if (!auth || !auth.startsWith('Bearer ')) return null;
    return auth.slice(7);
}

// Базовый middleware аутентификации
export const authenticate = async (
    req: Request, res: Response, next: NextFunction
) => {
    const token = extractToken(req);
    if (!token) {
        return next(new AppError(401, 'Токен аутентификации отсутствует'));
    }

    try {
        const payload = jwt.verify(token, process.env.JWT_SECRET!) as JwtPayload;
        req.user = payload;
        next();
    } catch (err) {
        if (err instanceof jwt.TokenExpiredError) {
            return next(new AppError(401, 'Токен истёк'));
        }
        if (err instanceof jwt.JsonWebTokenError) {
            logger.warn({ token: token.slice(0, 20) + '...', err }, 'Invalid JWT');
            return next(new AppError(401, 'Невалидный токен'));
        }
        next(err);
    }
};

// Middleware проверки роли (вызывать ПОСЛЕ authenticate)
export const requireRole = (...roles: UserRole[]) =>
    (req: Request, res: Response, next: NextFunction) => {
        if (!req.user) {
            return next(new AppError(401, 'Не аутентифицирован'));
        }
        if (!roles.includes(req.user.role)) {
            logger.warn({
                userId: req.user.sub,
                role: req.user.role,
                required: roles,
                path: req.path,
            }, 'Forbidden access attempt');
            return next(new AppError(403, 'Недостаточно прав доступа'));
        }
        next();
    };

// IDOR-защита: проверяем что пользователь обращается к своим ресурсам
export const requireOwnership = (
    extractOwnerId: (req: Request) => number | Promise<number>
) =>
    async (req: Request, res: Response, next: NextFunction) => {
        if (!req.user) return next(new AppError(401, 'Не аутентифицирован'));
        // superadmin может всё
        if (req.user.role === 'superadmin') return next();
        try {
            const ownerId = await extractOwnerId(req);
            if (ownerId !== req.user.sub) {
                logger.warn({ userId: req.user.sub, ownerId, path: req.path }, 'IDOR attempt');
                return next(new AppError(403, 'Нет доступа к этому ресурсу'));
            }
            next();
        } catch (err) {
            next(err);
        }
    };