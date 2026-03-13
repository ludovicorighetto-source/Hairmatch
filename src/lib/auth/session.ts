import { decodeJwt } from "jose";
import type { JWTPayload, AuthUser } from "@/types/auth";

/**
 * Decode JWT payload without verifying signature.
 * Signature verification happens server-side via the backend.
 */
export function decodeAccessToken(token: string): JWTPayload | null {
  try {
    const payload = decodeJwt(token) as JWTPayload;
    return payload;
  } catch {
    return null;
  }
}

/**
 * Returns true if the token expires within the given threshold (seconds).
 */
export function isTokenExpiringSoon(
  token: string,
  thresholdSeconds: number = 60
): boolean {
  const payload = decodeAccessToken(token);
  if (!payload) return true;
  const nowSeconds = Math.floor(Date.now() / 1000);
  return payload.exp - nowSeconds < thresholdSeconds;
}

/**
 * Returns true if the token is already expired.
 */
export function isTokenExpired(token: string): boolean {
  const payload = decodeAccessToken(token);
  if (!payload) return true;
  const nowSeconds = Math.floor(Date.now() / 1000);
  return payload.exp <= nowSeconds;
}

/**
 * Extract user info from the JWT payload.
 */
export function userFromToken(token: string): AuthUser | null {
  const payload = decodeAccessToken(token);
  if (!payload) return null;
  return {
    id: payload.sub,
    email: payload.email,
    role: payload.role,
    is_verified: true,
    is_active: true,
  };
}

/**
 * Seconds until token expiry. Returns 0 if expired or invalid.
 */
export function secondsUntilExpiry(token: string): number {
  const payload = decodeAccessToken(token);
  if (!payload) return 0;
  const nowSeconds = Math.floor(Date.now() / 1000);
  return Math.max(0, payload.exp - nowSeconds);
}
