import type {
  SalonProfile,
  ProfessionalProfile,
  UpdateSalonProfileRequest,
  UpdateProfessionalProfileRequest,
  PublicProfile,
} from "@/types/profile";
import { useAuthStore } from "@/lib/auth/store";

const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";
const API_PREFIX = "/api/v1/profiles";

async function profileFetch<T>(
  endpoint: string,
  options: RequestInit = {}
): Promise<T> {
  const store = useAuthStore.getState();
  const headers: Record<string, string> = {
    "Content-Type": "application/json",
    ...(options.headers as Record<string, string>),
  };

  if (store.accessToken) {
    headers["Authorization"] = `Bearer ${store.accessToken}`;
  }

  const response = await fetch(`${API_BASE_URL}${API_PREFIX}${endpoint}`, {
    ...options,
    headers,
    credentials: "include",
  });

  if (!response.ok) {
    const data = await response.json().catch(() => ({ detail: "Errore sconosciuto" }));
    const message =
      typeof data.detail === "string"
        ? data.detail
        : Array.isArray(data.detail)
        ? data.detail.map((e: { msg: string }) => e.msg).join(", ")
        : `Errore ${response.status}`;
    throw new Error(message);
  }

  return response.json() as Promise<T>;
}

export async function apiUpdateSalonProfile(
  data: UpdateSalonProfileRequest
): Promise<SalonProfile> {
  return profileFetch<SalonProfile>("/me/salon", {
    method: "PATCH",
    body: JSON.stringify(data),
  });
}

export async function apiUpdateProfessionalProfile(
  data: UpdateProfessionalProfileRequest
): Promise<ProfessionalProfile> {
  return profileFetch<ProfessionalProfile>("/me/professional", {
    method: "PATCH",
    body: JSON.stringify(data),
  });
}

export async function apiGetPublicProfile(userId: string): Promise<PublicProfile> {
  const response = await fetch(`${API_BASE_URL}${API_PREFIX}/${userId}`);
  if (!response.ok) {
    throw new Error(`Profilo non trovato (${response.status})`);
  }
  return response.json() as Promise<PublicProfile>;
}
