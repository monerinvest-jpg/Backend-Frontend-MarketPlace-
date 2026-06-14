import { Request, Response, NextFunction } from 'express';
import { ProductRepository } from '../repositories/product.repository';
import { OrderRepository } from '../repositories/order.repository';
import { AppError } from '../utils/AppError';

/** Проверяет, что текущий пользователь является владельцем продукта */
export const requireProductOwnership = async (
    req: Request,
    res: Response,
    next: NextFunction
): Promise<void> => {
    try {
        const productId = parseInt(req.params.id, 10);
        const userId = req.user!.id;
        const userRole = req.user!.role;

        // Суперадмин и модератор имеют доступ ко всему
        if (['superadmin', 'moderator'].includes(userRole)) {
            return next();
        }

        const product = await ProductRepository.findById(productId);
        if (!product) throw new AppError('Продукт не найден', 404);

        // Проверяем: seller должен владеть магазином, которому принадлежит продукт
        const shop = await ShopRepository.findByOwnerId(userId);
        if (!shop || shop.id !== product.shopId) {
            throw new AppError('Доступ запрещён', 403);
        }

        next();
    } catch (err) {
        next(err);
    }
};

/** Проверяет, что текущий пользователь является владельцем заказа */
export const requireOrderOwnership = async (
    req: Request,
    res: Response,
    next: NextFunction
): Promise<void> => {
    try {
        const orderId = parseInt(req.params.id, 10);
        const userId = req.user!.id;
        const userRole = req.user!.role;

        if (['superadmin', 'moderator'].includes(userRole)) return next();

        const order = await OrderRepository.findById(orderId);
        if (!order) throw new AppError('Заказ не найден', 404);

        // Buyer видит только свои заказы, seller — только заказы своего магазина
        if (userRole === 'buyer' && order.buyerId !== userId) {
            throw new AppError('Доступ запрещён', 403);
        }

        next();
    } catch (err) {
        next(err);
    }
};

// Применение:
// router.put('/:id', authMiddleware, roleGuard('seller'), requireProductOwnership, validate(...), controller.update);
// router.delete('/:id', authMiddleware, roleGuard('seller'), requireProductOwnership, controller.delete);