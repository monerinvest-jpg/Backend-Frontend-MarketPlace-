// ✅ backend/src/validators/product.validator.ts
// Полные Zod-схемы валидации для CRUD товаров

import { z } from 'zod';

// Базовая схема товара
const productBodySchema = z.object({
    title: z
        .string({ required_error: 'Название обязательно' })
        .min(3, 'Минимум 3 символа')
        .max(200, 'Максимум 200 символов')
        .trim(),

    description: z
        .string({ required_error: 'Описание обязательно' })
        .min(10, 'Минимум 10 символов')
        .max(5000, 'Максимум 5000 символов')
        .trim(),

    price: z
        .number({ required_error: 'Цена обязательна' })
        .positive('Цена должна быть положительной')
        .max(10_000_000, 'Максимальная цена 10 000 000'),

    quantity: z
        .number()
        .int('Количество должно быть целым числом')
        .nonnegative('Количество не может быть отрицательным')
        .max(100_000, 'Максимум 100 000 единиц'),

    categoryId: z
        .number({ required_error: 'Категория обязательна' })
        .int()
        .positive(),
});

export const createProductSchema = z.object({
    body: productBodySchema,
});

export const updateProductSchema = z.object({
    params: z.object({
        id: z.string().regex(/^\d+$/, 'ID должен быть числом').transform(Number),
    }),
    body: productBodySchema.partial(), // Все поля опциональны при обновлении
});

export const listProductsSchema = z.object({
    query: z.object({
        page: z.string().regex(/^\d+$/).transform(Number).default('1'),
        limit: z.string().regex(/^\d+$/).transform(Number).default('20').pipe(
            z.number().max(100, 'Максимум 100 элементов на странице')
        ),
        categoryId: z.string().regex(/^\d+$/).transform(Number).optional(),
        minPrice: z.string().regex(/^\d+(\.\d+)?$/).transform(Number).optional(),
        maxPrice: z.string().regex(/^\d+(\.\d+)?$/).transform(Number).optional(),
        search: z.string().max(100).trim().optional(),
        sortBy: z.enum(['price', 'rating', 'createdAt']).default('createdAt'),
        order: z.enum(['asc', 'desc']).default('desc'),
    }),
});

// Middleware для применения валидации
export const validate = (schema: z.ZodSchema) =>
    (req: Request, res: Response, next: NextFunction) => {
        const result = schema.safeParse({
            body: req.body,
            params: req.params,
            query: req.query,
        });

        if (!result.success) {
            return res.status(400).json({
                status: 'error',
                message: 'Ошибка валидации',
                errors: result.error.flatten(),
            });
        }

        // Присваиваем валидированные данные
        if (result.data.body) req.body = result.data.body;
        if (result.data.params) req.params = result.data.params;
        if (result.data.query) req.query = result.data.query;

        next();
    };