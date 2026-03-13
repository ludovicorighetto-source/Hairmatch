import type { AvailabilityStatus } from "@/types/search";
import type { JobStatus } from "@/types/jobs";

const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";
const BASE = `${API_BASE_URL}/api/v1/matching`;

async function matchFetch<T>(path: string, token: string): Promise<T> {
  const resp = await fetch(`${BASE}${path}`, {
    headers: { Authorization: `Bearer ${token}` },
    cache: "no-store",
  });
  if (!resp.ok) {
    const detail = await resp.json().catch(() => ({ detail: resp.statusText }));
    throw new Error(detail?.detail || `HTTP ${resp.status}`);
  }
  return resp.json() as Promise<T>;
}

export interface ScoreBreakdown {
  specialization: number;
  location: number;
  experience: number;
  availability: number;
}

export interface JobScoreBreakdown {
  specialization: number;
  location: number;
  contract_type: number;
}

export interface MatchedProfessional {
  user_id: string;
  first_name: string;
  last_name: string;
  specializations: string[];
  years_of_experience: number | null;
  availability_status: AvailabilityStatus;
  preferred_city: string | null;
  preferred_province: string | null;
  bio: string | null;
  profile_photo_url: string | null;
  is_featured: boolean;
  match_score: number;
  score_breakdown: ScoreBreakdown;
}

export interface MatchedJob {
  id: string;
  salon_id: string;
  title: string;
  description: string;
  specializations: string[];
  contract_types: string[];
  city: string | null;
  province: string | null;
  salary_min: number | null;
  salary_max: number | null;
  status: JobStatus;
  match_score: number;
  score_breakdown: JobScoreBreakdown;
}

export async function apiTopProfessionals(
  token: string,
  specializations?: string[],
  limit = 10
): Promise<MatchedProfessional[]> {
  const q = new URLSearchParams({ limit: String(limit) });
  specializations?.forEach((s) => q.append("specializations", s));
  return matchFetch(`/professionals?${q.toString()}`, token);
}

export async function apiRecommendedJobs(
  token: string,
  limit = 10
): Promise<MatchedJob[]> {
  return matchFetch(`/jobs?limit=${limit}`, token);
}
