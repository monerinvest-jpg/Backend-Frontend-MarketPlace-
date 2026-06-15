// frontend/src/store/authStore.ts — ИСПРАВЛЕНИЕ (без PII в localStorage)

import { create } from "zustand";
import { persist } from "zustand/middleware";
import { z } from "zod";

// ── Схема валидации форм ─────────────────────────────────────────────
export const loginSchema = z.object({
    email: z.string().email("Некорректный email").max(255),
    password: z.string().min(8, "Минимум 8 символов").max(128),
});

export const registerSchema = z.object({
    email: z.string().email("Некорректный email").max(255),
    password: z.string().min(8, "Минимум 8 символов").max(128),
    full_name: z.string().min(2, "Минимум 2 символа").max(255),
    referral_code: z.string().max(20).optional(),
});

// ── Token Service (in-memory, не localStorage) ───────────────────────
let _accessToken: string | null = null;

export const tokenService = {
    get: (): string | null => _accessToken,
    set: (token: string): void => {
        // Валидация формата JWT
        if (!token || token.split(".").length !== 3) {
            console.error("[TokenService] Invalid JWT format");
            return;
        }
        _accessToken = token;
    },
    clear: (): void => {
        _accessToken = null;
    },
    isExpired: (): boolean => {
        if (!_accessToken) return true;
        try {
            const payload = JSON.parse(atob(_accessToken.split(".")[1]));
            return Date.now() >= payload.exp * 1000;
        } catch {
            return true;
        }
    },
};

// ── Типы ─────────────────────────────────────────────────────────────
interface UserProfile {
    id: number;
    email: string;
    full_name: string;
    role: string;
}

interface AuthState {
    currentUser: UserProfile | null;
    isAuthenticated: boolean;
    wasAuthenticated: boolean;  // для UX при reload
    setUser: (user: UserProfile, token: string) => void;
    clear: () => void;
}

// ── Store ─────────────────────────────────────────────────────────────
export const useAuthStore = create<AuthState>()(
    persist(
        (set) => ({
            currentUser: null,
            isAuthenticated: false,
            wasAuthenticated: false,

            setUser: (user: UserProfile, token: string) => {
                tokenService.set(token);
                set({ currentUser: user, isAuthenticated: true, wasAuthenticated: true });
            },

            clear: () => {
                tokenService.clear();
                set({ currentUser: null, isAuthenticated: false });
            },
        }),
        {
            name: "auth-session",
            // ✅ Храним ТОЛЬКО флаг (без email, role, id!)
            // При reload делаем GET /auth/me для верификации
            partialize: (state) => ({
                wasAuthenticated: state.isAuthenticated,
                // ❌ НЕ: email, id, role, balance
            }),
            onRehydrateStorage: () => (state) => {
                // При загрузке из localStorage — всегда требуем верификации через API
                if (state?.wasAuthenticated) {
                    state.isAuthenticated = false;  // Будет восстановлен через /auth/me
                }
            },
        }
    )
);