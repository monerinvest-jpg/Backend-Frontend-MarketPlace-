import { create } from "zustand";
import { persist } from "zustand/middleware";
import { users } from "@/data/mockData";
import type { User, UserRole } from "@/types";

interface AuthState {
  currentUser: User | null;
  login: (email: string, role?: UserRole) => void;
  logout: () => void;
}

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
export const useAuthStore = create<AuthState>()((set) => ({
    currentUser: null,
    isAuthenticated: false,
    // ...
}));
