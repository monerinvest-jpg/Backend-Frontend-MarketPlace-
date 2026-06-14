import jwt from 'jsonwebtoken';
import crypto from 'crypto';
import { redisClient } from '../config/redis';
import { env } from '../config/validateEnv';

const ACCESS_TOKEN_TTL = '15m';
const REFRESH_TOKEN_TTL = 7 * 24 * 60 * 60; // 7 дней в секундах

interface TokenPayload {
    sub: string;       // userId
    email: string;
    role: string;
    jti: string;       // JWT ID для revocation
}

export class TokenService {
    /** Создаёт access + refresh токены */
    static async createTokenPair(userId: string, email: string, role: string) {
        const jti = crypto.randomUUID();

        const accessToken = jwt.sign(
            { sub: userId, email, role, jti },
            env.JWT_SECRET,
            { expiresIn: ACCESS_TOKEN_TTL, algorithm: 'HS256' }
        );

        // Refresh token — криптографически случайная строка (НЕ JWT)
        const refreshToken = crypto.randomBytes(64).toString('hex');

        // Сохраняем refresh token в Redis (белый список)
        // Ключ: refresh:userId:token → значение: jti (связанный access token)
        await redisClient.setEx(
            `refresh:${userId}:${refreshToken}`,
            REFRESH_TOKEN_TTL,
            JSON.stringify({ jti, email, role }),
        );

        return { accessToken, refreshToken };
    }

    /** Ротация: обменивает старый refresh token на новую пару */
    static async rotateRefreshToken(oldRefreshToken: string, userId: string) {
        const key = `refresh:${userId}:${oldRefreshToken}`;
        const stored = await redisClient.get(key);
        if (!stored) throw new Error('Недействительный refresh token');

        const { email, role } = JSON.parse(stored);

        // Инвалидируем старый токен (rotation!)
        await redisClient.del(key);

        // Выдаём новую пару
        return this.createTokenPair(userId, email, role);
    }

    /** Выход: инвалидируем все токены пользователя */
    static async revokeAllTokens(userId: string) {
        const keys = await redisClient.keys(`refresh:${userId}:*`);
        if (keys.length) await redisClient.del(keys);
    }

    /** Верификация access token */
    static verifyAccessToken(token: string): TokenPayload {
        return jwt.verify(token, env.JWT_SECRET) as TokenPayload;
    }
}