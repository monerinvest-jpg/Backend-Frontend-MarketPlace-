import { Request, Response, NextFunction } from 'express';
import { ZodSchema, ZodError } from 'zod';

type Target = 'body' | 'query' | 'params';

export const validate = (schema: ZodSchema, target: Target = 'body') =>
    (req: Request, res: Response, next: NextFunction): void => {
        const result = schema.safeParse(req[target]);
        if (!result.success) {
            res.status(400).json({
                error: 'Ошибка валидации',
                details: result.error.errors.map(e => ({
                    field: e.path.join('.'),
                    message: e.message,
                })),
            });
            return;
        }
        // Перезаписываем req[target] распарсенными (sanitized) данными
        req[target] = result.data;
        next();
    };

// ── Схемы валидации ──────────────────────────────────────────────
// backend/src/validators/product.validator.ts
import { z } from 'zod';

export const createProductSchema = z.object({
    title: z.string().min(3).max(200).trim(),
    description: z.string().min(10).max(5000).trim(),
    price: z.number().positive().max(10_000_000),
    quantity: z.number().int().min(0).max(99_999),
    categoryId: z.number().int().positive(),
    // imageUrl валидируется отдельно через multer!
});

export const productQuerySchema = z.object({
    page: z.coerce.number().int().min(1).default(1),
    limit: z.coerce.number().int().min(1).max(100).default(20),
    categoryId: z.coerce.number().int().positive().optional(),
    search: z.string().max(100).trim().optional(),
    sortBy: z.enum(['price', 'rating', 'createdAt']).default('createdAt'),
    order: z.enum(['asc', 'desc']).default('desc'),
});

// ── Применение на маршрутах ──────────────────────────────────────
// backend/src/routes/product.routes.ts
import { validate } from '../middleware/validate.middleware';
import { createProductSchema, productQuerySchema } from '../validators/product.validator';

router.get('/', validate(productQuerySchema, 'query'), productController.list);
router.post('/', authMiddleware, roleGuard('seller'), validate(createProductSchema), productController.create);