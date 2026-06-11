// ✅ backend/src/services/auth.service.ts
// Полный сервис аутентификации

import bcrypt from 'bcrypt';
import jwt from 'jsonwebtoken';
import crypto from 'crypto';
import { redis } from '../config/redis';
import { db } from '../config/database';
import { AppError } from '../middleware/error.middleware';
import type { JwtPayload } from '../middleware/auth.middleware';

const BCRYPT_ROUNDS = parseInt(process.env.BCRYPT_ROUNDS || '12');
const ACCESS_SECRET = process.env.JWT_SECRET!;
const REFRESH_SECRET = process.env.JWT_REFRESH_SECRET!;
const ACCESS_EXPIRES = process.env.JWT_ACCESS_EXPIRES || '15m';
const REFRESH_EXPIRES = process.env.JWT_REFRESH_EXPIRES || '7d';
const REFRESH_TTL = parseInt(process.env.REDIS_REFRESH_TOKEN_TTL || '604800');

export class AuthService {
    // Хеширование пароля
    async hashPassword(password: string): Promise<string> {
        return bcrypt.hash(password, BCRYPT_ROUNDS);
    }

    // Проверка пароля
    async verifyPassword(password: string, hash: string): Promise<boolean> {
        return bcrypt.compare(password, hash);
    }

    // Генерация JWT пары токенов
    generateTokens(userId: number, email: string, role: string): {
        accessToken: string;
        refreshToken: string;
        jti: string;
    } {
        const jti = crypto.randomUUID();
        const payload = { sub: userId, email, role, jti };

        const accessToken = jwt.sign(payload, ACCESS_SECRET, {
            expiresIn: ACCESS_EXPIRES as any,
            issuer: 'marketplace-api',
            audience: 'marketplace-client',
        });

        const refreshToken = jwt.sign(
            { sub: userId, jti },
            REFRESH_SECRET,
            { expiresIn: REFRESH_EXPIRES as any }
        );

        return { accessToken, refreshToken, jti };
    }

    // Сохранение refresh token в Redis (с возможностью инвалидации)
    async saveRefreshToken(userId: number, jti: string): Promise<void> {
        await redis.set(
            `refresh:${userId}:${jti}`,
            '1',
            { EX: REFRESH_TTL }
        );
    }

    // Логин
    async login(email: string, password: string): Promise<{
        accessToken: string;
        refreshToken: string;
        user: Omit<User, 'passwordHash'>;
    }> {
        const user = await db('users').where({ email }).first();

        // ✅ Не говорим, что именно не так (email или пароль)
        if (!user) {
            await bcrypt.hash(password, BCRYPT_ROUNDS); // Timing attack protection
            throw new AppError(401, 'Неверный email или пароль');
        }

        if (!user.isActive) {
            throw new AppError(403, 'Аккаунт заблокирован');
        }

        // Проверяем блокировку после брутфорса
        if (user.lockedUntil && new Date(user.lockedUntil) > new Date()) {
            throw new AppError(429, 'Аккаунт временно заблокирован');
        }

        const isValid = await this.verifyPassword(password, user.passwordHash);

        if (!isValid) {
            await db('users')
                .where({ id: user.id })
                .increment('failedLoginAttempts', 1);

            // Блокируем после 5 неудачных попыток
            if (user.failedLoginAttempts + 1 >= 5) {
                const lockUntil = new Date(Date.now() + 30 * 60 * 1000); // 30 минут
                await db('users').where({ id: user.id }).update({ lockedUntil: lockUntil });
            }
            throw new AppError(401, 'Неверный email или пароль');
        }

        // Сбрасываем счётчик при успешном логине
        await db('users').where({ id: user.id }).update({
            failedLoginAttempts: 0,
            lockedUntil: null,
            lastLoginAt: new Date(),
        });

        const { accessToken, refreshToken, jti } = this.generateTokens(
            user.id, user.email, user.role
        );
        await this.saveRefreshToken(user.id, jti);

        const { passwordHash, ...safeUser } = user;
        return { accessToken, refreshToken, user: safeUser };
    }

    // Обновление access token по refresh token
    async refreshTokens(refreshToken: string): Promise<{
        accessToken: string;
        refreshToken: string;
    }> {
        let payload: any;
        try {
            payload = jwt.verify(refreshToken, REFRESH_SECRET);
        } catch {
            throw new AppError(401, 'Невалидный refresh token');
        }

        // Проверяем, что токен ещё в Redis (не инвалидирован)
        const exists = await redis.get(`refresh:${payload.sub}:${payload.jti}`);
        if (!exists) {
            throw new AppError(401, 'Refresh token отозван');
        }

        // Удаляем старый токен (rotation)
        await redis.del(`refresh:${payload.sub}:${payload.jti}`);

        const user = await db('users').where({ id: payload.sub }).first();
        if (!user || !user.isActive) throw new AppError(401, 'Пользователь не найден');

        const { accessToken, refreshToken: newRefresh, jti } = this.generateTokens(
            user.id, user.email, user.role
        );
        await this.saveRefreshToken(user.id, jti);

        return { accessToken, refreshToken: newRefresh };
    }

    // Выход (инвалидация всех токенов пользователя)
    async logout(userId: number, jti: string): Promise<void> {
        await redis.del(`refresh:${userId}:${jti}`);
    }
}