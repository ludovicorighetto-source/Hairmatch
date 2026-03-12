import type {
  LoginRequest,
  LoginResponse,
  SalonRegisterRequest,
  ProfessionalRegisterRequest,
  RegisterResponse,
  RefreshResponse,
  ApiError,
} from "@/types/auth";
import { useAuthStore } from "@/lib/auth/store";

const API_BASE_URL =
  process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";
const API_PREFIX = "/api/v1/auth";
const REQUEST_TIMEOUT_MS = 10_000;

export class ApiRequestError extends Error {
  constructor(
    public readonly statusCode: number,
    message: string,
    public readonly detail?: string | unknown
  ) {
    super(message);
    this.name = "ApiRequestError";
  }
}

async function fetchWithTimeout(
  url: string,
  options: RequestInit,
  timeoutMs: number = REQUEST_TIMEOUT_MS
): Promise<Response> {
  const controller = new AbortController();
  const timeoutId = setTimeout(() => controller.abort(), timeoutMs);

  try {
    const response = await fetch(url, {
      ...options,
      signal: controller.signal,
    });
    return response;
  } finally {
    clearTimeout(timeoutId);
  }
}

async function parseErrorResponse(response: Response): Promise<string> {
  try {
    const data = (await response.json()) as ApiError;
    if (typeof data.detail === "string") {
      return data.detail;
    }
    if (Array.isArray(data.detail)) {
      return data.detail.map((e) => e.msg).join(", ");
    }
    return `Errore ${response.status}`;
  } catch {
    return `Errore ${response.status}: ${response.statusText}`;
  }
}

/**
 * Core fetch wrapper. Handles auth header injection and 401 refresh retry.
 */
async function apiFetch<T>(
  endpoint: string,
  options: RequestInit & { skipAuth?: boolean; isRetry?: boolean } = {}
): Promise<T> {
  const { skipAuth = false, isRetry = false, ...fetchOptions } = options;
  const url = `${API_BASE_URL}${API_PREFIX}${endpoint}`;

  const headers: Record<string, string> = {
    "Content-Type": "application/json",
    ...(fetchOptions.headers as Record<string, string>),
  };

  // Inject access token from store if available
  if (!skipAuth) {
    // We access store directly to avoid hook rules issues
    const store = useAuthStore.getState();
    if (store.accessToken) {
      headers["Authorization"] = `Bearer ${store.accessToken}`;
    }
  }

  let response: Response;
  try {
    response = await fetchWithTimeout(url, {
      ...fetchOptions,
      headers,
      credentials: "include", // include cookies for refresh token
    });
  } catch (err) {
    if (err instanceof Error && err.name === "AbortError") {
      throw new ApiRequestError(408, "La richiesta ha impiegato troppo tempo. Riprova.");
    }
    throw new ApiRequestError(0, "Impossibile connettersi al server. Controlla la tua connessione.");
  }

  // Handle 401: attempt token refresh and retry once
  if (response.status === 401 && !isRetry && !skipAuth) {
    try {
      const store = useAuthStore.getState();
      await store.refreshToken();
      return apiFetch<T>(endpoint, { ...options, isRetry: true });
    } catch {
      // Refresh failed — auth store will handle clearing state
      throw new ApiRequestError(401, "Sessione scaduta. Effettua di nuovo il login.");
    }
  }

  if (!response.ok) {
    const message = await parseErrorResponse(response);
    throw new ApiRequestError(response.status, message, message);
  }

  // Handle empty body (e.g. 204 No Content)
  const contentType = response.headers.get("content-type");
  if (!contentType || !contentType.includes("application/json")) {
    return undefined as unknown as T;
  }

  return response.json() as Promise<T>;
}

// ─── Auth endpoints ────────────────────────────────────────────────────────────

export async function apiLogin(data: LoginRequest): Promise<LoginResponse> {
  return apiFetch<LoginResponse>("/login", {
    method: "POST",
    body: JSON.stringify(data),
    skipAuth: true,
  });
}

export async function apiRegisterSalon(
  data: SalonRegisterRequest
): Promise<RegisterResponse> {
  return apiFetch<RegisterResponse>("/register/salon", {
    method: "POST",
    body: JSON.stringify(data),
    skipAuth: true,
  });
}

export async function apiRegisterProfessional(
  data: ProfessionalRegisterRequest
): Promise<RegisterResponse> {
  return apiFetch<RegisterResponse>("/register/professional", {
    method: "POST",
    body: JSON.stringify(data),
    skipAuth: true,
  });
}

export async function apiRefreshToken(): Promise<RefreshResponse> {
  return apiFetch<RefreshResponse>("/refresh", {
    method: "POST",
    skipAuth: true,
    // Refresh token is sent automatically via HttpOnly cookie
  });
}

export async function apiLogout(): Promise<void> {
  return apiFetch<void>("/logout", {
    method: "POST",
  });
}

export async function apiResendVerification(email: string): Promise<{ message: string }> {
  return apiFetch<{ message: string }>("/resend-verification", {
    method: "POST",
    body: JSON.stringify({ email }),
    skipAuth: true,
  });
}
