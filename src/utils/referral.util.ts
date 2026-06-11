import crypto from 'crypto';

export function generateReferralCode(length = 12): string {
    // Криптографически случайный код
    return crypto.randomBytes(length)
        .toString('base64url')
        .slice(0, length)
        .toUpperCase();
}
// Пример: "X7K2MNP4QR8A" — не предсказуемо