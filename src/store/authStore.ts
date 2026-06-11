import { create } from "zustand";
import { persist } from "zustand/middleware";
import { users } from "@/data/mockData";
import type { User, UserRole } from "@/types";

interface AuthState {
  currentUser: User | null;
  login: (email: string, role?: UserRole) => void;
  logout: () => void;
}

export const useAuthStore = create<AuthState>()(
  persist(
    (set) => ({
      currentUser: users[2],
      login: (email, role) => {
        const byEmail = users.find((item) => item.email === email);
        const byRole = role ? users.find((item) => item.role === role) : null;
        set({ currentUser: byRole ?? byEmail ?? users[2] });
      },
      logout: () => set({ currentUser: null }),
    }),
    { name: "marketplace-auth" }
  )
);
