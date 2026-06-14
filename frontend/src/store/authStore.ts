import { create } from "zustand";
import { persist } from "zustand/middleware";
import { users } from "@/data/mockData";
import type { User, UserRole } from "@/types";
import { z } from 'zod';
import { create } from "zustand";
import { persist } from "zustand/middleware";
import type { User } from "@/types";

export const loginSchema = z.object({
    email: z.string().email('Некорректный email').max(255),
    password: z.string().min(8, 'Минимум 8 символов').max(128),
});

// В store — только данные профиля (без роли в параметрах)
login: (credentials: z.infer<typeof loginSchema>) => Promise<void>;

// ── Единственная реализация TokenService ──────────────────
// Access token: ТОЛЬКО в памяти (in-memory), НЕ в localStorage
let _accessToken: string | null = null;

export const tokenService = {
    get: (): string | null => _accessToken,
    set: (token: string): void => {
        // Валидация формата JWT перед сохранением
        if (!token || token.split('.').length !== 3) {
            console.error('[TokenService] Invalid JWT format');
            return;
        }
        _accessToken = token;
    },
    clear: (): void => { _accessToken = null; },
    isExpired: (): boolean => {
        if (!_accessToken) return true;
        try {
            const payload = JSON.parse(atob(_accessToken.split('.')[1]));
            return Date.now() >= payload.exp * 1000;
        } catch { return true; }
    },
};

// Refresh token управляется ТОЛЬКО через HttpOnly cookie на бэкенде
// Set-Cookie: refreshToken=...; HttpOnly; Secure; SameSite=Strict; Path=/api/v1/auth/refresh

interface AuthState {
    currentUser: Pick<User, 'id' | 'email' | 'role'> | null;
    isAuthenticated: boolean;
    setUser: (user: Pick<User, 'id' | 'email' | 'role'>, token: string) => void;
    clear: () => void;
}

export const useAuthStore = create<AuthState>()(
    persist(
        (set, get) => ({
            currentUser: null,
            isAuthenticated: false,
            setUser: (user, token) => {
                tokenService.set(token);
                set({ currentUser: user, isAuthenticated: true });
            },
            clear: () => {
                tokenService.clear();
                set({ currentUser: null, isAuthenticated: false });
            },
        }),
        {
            name: "auth-session",
            // ✅ Храним ТОЛЬКО то, что нужно для UX (имя для отображения)
            // ✅ НЕ храним: role, balance, referralCode
            partialize: (state) => ({
                currentUser: state.currentUser
                    ? { id: state.currentUser.id, email: state.currentUser.email }
                    : null,
            }),
            // При загрузке из localStorage — всегда верифицируем через API
            onRehydrateStorage: () => (state) => {
                if (state?.currentUser) {
                    // Помечаем как "требует верификации"
                    state.isAuthenticated = false; // API подтвердит
                }
            },
        }
    )
);