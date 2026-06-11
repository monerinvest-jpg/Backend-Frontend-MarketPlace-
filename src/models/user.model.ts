import bcrypt from 'bcrypt';

interface UserModel {
    id: number;
    email: string;
    fullName: string;
    passwordHash: string; // ТОЛЬКО хеш, никогда plaintext!
    role: UserRole;
    referralCode: string;
    isActive: boolean;
    failedLoginAttempts: number;
    lockedUntil: Date | null;
    createdAt: Date;
    updatedAt: Date;
}

// backend/src/services/auth.service.ts
export class AuthService {
    async hashPassword(password: string): Promise<string> {
        const COST_FACTOR = 12;
        return bcrypt.hash(password, COST_FACTOR);
    }

    async verifyPassword(password: string, hash: string): Promise<boolean> {
        return bcrypt.compare(password, hash);
    }
}