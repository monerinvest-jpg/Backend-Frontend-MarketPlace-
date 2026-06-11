import helmet from 'helmet';
import cors from 'cors';

export const securityMiddleware = [
    helmet({
        contentSecurityPolicy: {
            directives: {
                defaultSrc: ["'self'"],
                scriptSrc: ["'self'"],
                styleSrc: ["'self'", "'unsafe-inline'"],
                imgSrc: ["'self'", "data:", "https://images.unsplash.com"],
                connectSrc: ["'self'", process.env.API_URL!],
                frameSrc: ["'none'"],
            },
        },
        hsts: { maxAge: 31536000, includeSubDomains: true, preload: true },
        noSniff: true,
        xssFilter: true,
        referrerPolicy: { policy: 'strict-origin-when-cross-origin' },
    }),
    cors({
        origin: (origin, callback) => {
            const allowed = (process.env.ALLOWED_ORIGINS || '').split(',');
            if (!origin || allowed.includes(origin)) return callback(null, true);
            callback(new Error('Not allowed by CORS'));
        },
        credentials: true,
        methods: ['GET', 'POST', 'PUT', 'PATCH', 'DELETE'],
        allowedHeaders: ['Content-Type', 'Authorization'],
    }),
];