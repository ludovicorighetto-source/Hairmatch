import { create } from "zustand";
import type { AuthUser } from "@/types/auth";

/**
 * Raw Zustand store shape — no API calls here to avoid circular deps.
 * Actions that call the API are wired in context.tsx.
 */
interface AuthStoreState {
  user: AuthUser | null;
  accessToken: string | null;
  isLoading: boolean;
  isAuthenticated: boolean;
  // Placeholder actions — overridden in AuthProvider / context
  login: (email: string, password: string) => Promise<void>;
  logout: () => Promise<void>;
  refreshToken: () => Promise<void>;
  setUser: (user: AuthUser | null, accessToken: string | null) => void;
}

export const useAuthStore = create<AuthStoreState>((set) => ({
  user: null,
  accessToken: null,
  isLoading: true,
  isAuthenticated: false,

  setUser: (user: AuthUser | null, accessToken: string | null) => {
    set({
      user,
      accessToken,
      isAuthenticated: user !== null && accessToken !== null,
      isLoading: false,
    });
  },

  // These will be overridden by the context wiring, but provide
  // safe no-op defaults so the store is always callable.
  login: async () => {
    throw new Error("AuthProvider not mounted");
  },
  logout: async () => {
    throw new Error("AuthProvider not mounted");
  },
  refreshToken: async () => {
    throw new Error("AuthProvider not mounted");
  },
}));
