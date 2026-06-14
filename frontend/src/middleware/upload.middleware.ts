import multer from 'multer';
import { fromBuffer } from 'file-type';
import path from 'path';

const ALLOWED_MIME_TYPES = ['image/jpeg', 'image/png', 'image/webp'];
const MAX_FILE_SIZE = 5 * 1024 * 1024; // 5MB

export const uploadMiddleware = multer({
    storage: multer.memoryStorage(),
    limits: { fileSize: MAX_FILE_SIZE, files: 1 },
    fileFilter: (req, file, cb) => {
        if (!ALLOWED_MIME_TYPES.includes(file.mimetype)) {
            return cb(new Error('Недопустимый тип файла'));
        }
        cb(null, true);
    },
});

// Дополнительная проверка magic bytes
export const validateFileType = async (buffer: Buffer): Promise<void> => {
    const fileType = await fromBuffer(buffer);
    if (!fileType || !ALLOWED_MIME_TYPES.includes(fileType.mime)) {
        throw new Error('Файл не является изображением');
    }
};