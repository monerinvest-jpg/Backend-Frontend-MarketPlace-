import crypto from 'crypto';
import { Request, Response, NextFunction } from 'express';
import helmet from 'helmet';

export const cspMiddleware = (req: Request, res: Response, next: NextFunction) => {
    const nonce = crypto.randomBytes(16).toString('base64');
    res.locals.nonce = nonce;

    helmet.contentSecurityPolicy({
        directives: {
            defaultSrc: ["'self'"],
            scriptSrc: ["'self'", `'nonce-${nonce}'`],
            styleSrc: ["'self'", "'unsafe-inline'"], // Tailwind требует
            imgSrc: ["'self'", "data:", "https://images.unsplash.com"],
            connectSrc: ["'self'", process.env.FRONTEND_URL ?? ''],
            fontSrc: ["'self'"],
            objectSrc: ["'none'"],
            frameAncestors: ["'none'"],  // ← защита от Clickjacking
            baseUri: ["'self'"],
            formAction: ["'self'"],
            upgradeInsecureRequests: process.env.NODE_ENV === 'production' ? [] : undefined,
        },
    })(req, res, next);
};