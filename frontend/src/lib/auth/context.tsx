"use client";

import React, { useEffect, useRef } from "react";
import { apiLogin, apiLogout, apiRefreshToken } from "@/lib/api/auth";
import { userFromToken, isTokenExpiringSoon } from "@/lib/auth/session";
import { useAuthStore } from "@/lib/auth/store";

export { useAuthStore } from "@/lib/auth/store";

/**
 * AuthProvider wires up real async actions into the store and handles:
 * 1. Initial session hydration via a silent refresh-token call on mount
 * 2. Proactive access-token refresh (every 60 s if token expires in <60 s)
 */
export function AuthProvider({ children }: { children: React.ReactNode }) {
  const initialized = useRef(false);

  // Wire up real actions once on mount
  useEffect(() => {
    useAuthStore.setState({
      login: async (email: string, password: string) => {
        useAuthStore.setState({ isLoading: true });
        try {
          const response = await apiLogin({ email, password });
          useAuthStore.setState({
            user: response.user,
            accessToken: response.access_token,
            isAuthenticated: true,
            isLoading: false,
          });
        } catch (err) {
          useAuthStore.setState({ isLoading: false });
          throw err;
        }
      },

      logout: async () => {
        useAuthStore.setState({ isLoading: true });
        try {
          await apiLogout();
        } catch {
          // Clear state even on API failure
        } finally {
          useAuthStore.setState({
            user: null,
            accessToken: null,
            isAuthenticated: false,
            isLoading: false,
          });
        }
      },

      refreshToken: async () => {
        try {
          const response = await apiRefreshToken();
          const user = userFromToken(response.access_token);
          useAuthStore.setState({
            accessToken: response.access_token,
            user,
            isAuthenticated: user !== null,
            isLoading: false,
          });
        } catch (err) {
          useAuthStore.setState({
            user: null,
            accessToken: null,
            isAuthenticated: false,
            isLoading: false,
          });
          throw err;
        }
      },
    });
  }, []);

  // Initial hydration: try to restore session via HttpOnly refresh-token cookie
  useEffect(() => {
    if (initialized.current) return;
    initialized.current = true;

    (async () => {
      try {
        await useAuthStore.getState().refreshToken();
      } catch {
        useAuthStore.getState().setUser(null, null);
      }
    })();
  }, []);

  // Proactive refresh every 60 s
  useEffect(() => {
    const intervalId = setInterval(async () => {
      const { accessToken, refreshToken } = useAuthStore.getState();
      if (!accessToken) return;

      if (isTokenExpiringSoon(accessToken, 60)) {
        try {
          await refreshToken();
        } catch {
          // Will be caught on next API call
        }
      }
    }, 60_000);

    return () => clearInterval(intervalId);
  }, []);

  return <>{children}</>;
}
