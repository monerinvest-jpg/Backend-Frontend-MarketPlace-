import { create } from "zustand";
import { persist } from "zustand/middleware";
import { users } from "@/data/mockData";
import type { User, UserRole } from "@/types";
import { z } from 'zod';

export const loginSchema = z.object({
    email: z.string().email('Ќекорректный email').max(255),
    password: z.string().min(8, 'ћинимум 8 символов').max(128),
});

// ¬ store Ч только данные профил€ (без роли в параметрах)
login: (credentials: z.infer<typeof loginSchema>) => Promise<void>;

// access token Ч только в пам€ти (переменна€ модул€)
let accessToken: string | null = null;

export const tokenService = {
    getAccessToken: () => accessToken,
    setAccessToken: (token: string) => { accessToken = token; },
    clearTokens: () => { accessToken = null; },
};

// refresh token Ч HttpOnly cookie (устанавливаетс€ сервером)
// Set-Cookie: refreshToken=...; HttpOnly; Secure; SameSite=Strict; Path=/auth/refresh

// Zustand без persist Ч только текущий пользователь в пам€ти
// access token Ч только в пам€ти модул€ (не в store, не в localStorage)
let _accessToken: string | null = null;

export const tokenService = {
    get: () => _accessToken,
    set: (t: string) => { _accessToken = t; },
    clear: () => { _accessToken = null; },
};

// ¬ store persist Ч только несекретные данные профил€
export const useAuthStore = create<AuthState>()(
    persist(
        (set) => ({
            currentUser: null, // { id, email, role } Ч не секрет
            isAuthenticated: false,
            setUser: (user) => set({ currentUser: user, isAuthenticated: true }),
            clear: () => { tokenService.clear(); set({ currentUser: null, isAuthenticated: false }); },
        }),
        {
            name: 'auth-profile', // только профиль, без токенов!
            partialize: (state) => ({ currentUser: state.currentUser }),
        }
    )
);
