import type { ProfessionalCard, SalonCard, PaginatedResult } from "@/types/search";

const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";

export interface SearchProfessionalsParams {
  city?: string;
  province?: string;
  specializations?: string[];
  availability_status?: string;
  page?: number;
  limit?: number;
}

export interface SearchSalonsParams {
  city?: string;
  province?: string;
  page?: number;
  limit?: number;
}

async function searchFetch<T>(path: string, params: Record<string, unknown>): Promise<T> {
  const query = new URLSearchParams();
  for (const [key, value] of Object.entries(params)) {
    if (value === undefined || value === null || value === "") continue;
    if (Array.isArray(value)) {
      value.forEach((v) => query.append(key, String(v)));
    } else {
      query.append(key, String(value));
    }
  }

  const url = `${API_BASE_URL}/api/v1/search${path}?${query.toString()}`;
  const resp = await fetch(url, { cache: "no-store" });

  if (!resp.ok) {
    throw new Error(`Search failed: ${resp.status}`);
  }
  return resp.json() as Promise<T>;
}

export async function apiSearchProfessionals(
  params: SearchProfessionalsParams
): Promise<PaginatedResult<ProfessionalCard>> {
  return searchFetch("/professionals", params as Record<string, unknown>);
}

export async function apiSearchSalons(
  params: SearchSalonsParams
): Promise<PaginatedResult<SalonCard>> {
  return searchFetch("/salons", params as Record<string, unknown>);
}
