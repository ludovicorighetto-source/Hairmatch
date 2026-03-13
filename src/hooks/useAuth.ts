"use client";

import { useAuthStore } from "@/lib/auth/store";

/**
 * useAuth — convenience hook exposing all auth state and actions.
 * Wraps the Zustand store so consumers don't import the store directly.
 */
export function useAuth() {
  const user = useAuthStore((s) => s.user);
  const accessToken = useAuthStore((s) => s.accessToken);
  const isLoading = useAuthStore((s) => s.isLoading);
  const isAuthenticated = useAuthStore((s) => s.isAuthenticated);
  const login = useAuthStore((s) => s.login);
  const logout = useAuthStore((s) => s.logout);
  const refreshToken = useAuthStore((s) => s.refreshToken);
  const setUser = useAuthStore((s) => s.setUser);

  return {
    user,
    accessToken,
    isLoading,
    isAuthenticated,
    login,
    logout,
    refreshToken,
    setUser,
  };
}
