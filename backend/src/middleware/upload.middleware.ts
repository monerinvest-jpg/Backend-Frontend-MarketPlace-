import multer from 'multer';
import path from 'path';
import crypto from 'crypto';
import { Request } from 'express';
import { AppError } from '../utils/AppError';

// Разрешённые MIME-типы и их magic bytes
const ALLOWED_MIME_TYPES: Record<string, Buffer> = {
    'image/jpeg': Buffer.from([0xFF, 0xD8, 0xFF]),
    'image/png': Buffer.from([0x89, 0x50, 0x4E, 0x47]),
    'image/webp': Buffer.from([0x52, 0x49, 0x46, 0x46]),
};

const MAX_FILE_SIZE = 5 * 1024 * 1024; // 5 MB
const MAX_FILES = 10;

// Проверка magic bytes (реальный тип файла)
const validateMagicBytes = (buffer: Buffer, mimeType: string): boolean => {
    const magic = ALLOWED_MIME_TYPES[mimeType];
    if (!magic) return false;
    return buffer.subarray(0, magic.length).equals(magic);
};

export const productImageUpload = multer({
    storage: multer.memoryStorage(), // В памяти для проверки magic bytes
    limits: {
        fileSize: MAX_FILE_SIZE,
        files: MAX_FILES,
        fields: 20,
    },
    fileFilter: (req: Request, file, cb) => {
        // 1. Проверяем MIME-тип из заголовка
        if (!Object.keys(ALLOWED_MIME_TYPES).includes(file.mimetype)) {
            return cb(new AppError(`Недопустимый тип файла: ${file.mimetype}`, 400) as any);
        }
        // 2. Проверяем расширение
        const ext = path.extname(file.originalname).toLowerCase();
        if (!['.jpg', '.jpeg', '.png', '.webp'].includes(ext)) {
            return cb(new AppError('Недопустимое расширение файла', 400) as any);
        }
        // Magic bytes проверяем после upload в контроллере
        cb(null, true);
    },
});

// ── В контроллере после multer ───────────────────────────────────
export const validateUploadedFile = (file: Express.Multer.File): void => {
    if (!validateMagicBytes(file.buffer, file.mimetype)) {
        throw new AppError('Файл повреждён или имеет неверный формат', 400);
    }

    // Генерируем безопасное имя файла (UUID + расширение)
    const ext = path.extname(file.originalname).toLowerCase();
    file.filename = `${crypto.randomUUID()}${ext}`;
};