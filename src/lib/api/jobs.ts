import type {
  JobPosting,
  JobPostingListResponse,
  CreateJobPostingRequest,
  UpdateJobPostingRequest,
  JobApplication,
  ApplicationWithJob,
} from "@/types/jobs";

const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";
const JOBS_BASE = `${API_BASE_URL}/api/v1/jobs`;

async function jobsFetch<T>(
  path: string,
  options: RequestInit = {}
): Promise<T> {
  const resp = await fetch(`${JOBS_BASE}${path}`, {
    ...options,
    headers: {
      "Content-Type": "application/json",
      ...(options.headers || {}),
    },
  });
  if (!resp.ok) {
    const detail = await resp.json().catch(() => ({ detail: resp.statusText }));
    throw new Error(detail?.detail || `HTTP ${resp.status}`);
  }
  if (resp.status === 204) return undefined as T;
  return resp.json() as Promise<T>;
}

// ── Salon: job postings ──────────────────────────────────────────────────────

export async function apiCreateJobPosting(
  token: string,
  data: CreateJobPostingRequest
): Promise<JobPosting> {
  return jobsFetch("/", {
    method: "POST",
    headers: { Authorization: `Bearer ${token}` },
    body: JSON.stringify(data),
  });
}

export async function apiListMyJobs(
  token: string,
  page = 1,
  limit = 20
): Promise<JobPostingListResponse> {
  return jobsFetch(`/mine?page=${page}&limit=${limit}`, {
    headers: { Authorization: `Bearer ${token}` },
    cache: "no-store",
  });
}

export async function apiUpdateJobPosting(
  token: string,
  jobId: string,
  data: UpdateJobPostingRequest
): Promise<JobPosting> {
  return jobsFetch(`/${jobId}`, {
    method: "PATCH",
    headers: { Authorization: `Bearer ${token}` },
    body: JSON.stringify(data),
  });
}

export async function apiDeleteJobPosting(
  token: string,
  jobId: string
): Promise<void> {
  return jobsFetch(`/${jobId}`, {
    method: "DELETE",
    headers: { Authorization: `Bearer ${token}` },
  });
}

export async function apiGetJobApplicants(
  token: string,
  jobId: string
): Promise<JobApplication[]> {
  return jobsFetch(`/${jobId}/applications`, {
    headers: { Authorization: `Bearer ${token}` },
    cache: "no-store",
  });
}

export async function apiUpdateApplicationStatus(
  token: string,
  appId: string,
  status: string
): Promise<JobApplication> {
  return jobsFetch(`/applications/${appId}/status`, {
    method: "PATCH",
    headers: { Authorization: `Bearer ${token}` },
    body: JSON.stringify({ status }),
  });
}

// ── Public: browse jobs ──────────────────────────────────────────────────────

export async function apiBrowseJobs(params: {
  city?: string;
  province?: string;
  specializations?: string[];
  contract_types?: string[];
  page?: number;
  limit?: number;
}): Promise<JobPostingListResponse> {
  const q = new URLSearchParams();
  if (params.city) q.set("city", params.city);
  if (params.province) q.set("province", params.province);
  if (params.page) q.set("page", String(params.page));
  if (params.limit) q.set("limit", String(params.limit));
  params.specializations?.forEach((s) => q.append("specializations", s));
  params.contract_types?.forEach((c) => q.append("contract_types", c));

  return jobsFetch(`/?${q.toString()}`, { cache: "no-store" });
}

// ── Professional: apply & track ───────────────────────────────────────────────

export async function apiApplyToJob(
  token: string,
  jobId: string,
  coverLetter?: string
): Promise<JobApplication> {
  return jobsFetch(`/${jobId}/apply`, {
    method: "POST",
    headers: { Authorization: `Bearer ${token}` },
    body: JSON.stringify({ cover_letter: coverLetter ?? null }),
  });
}

export async function apiMyApplications(
  token: string
): Promise<ApplicationWithJob[]> {
  return jobsFetch("/applications/mine", {
    headers: { Authorization: `Bearer ${token}` },
    cache: "no-store",
  });
}

export async function apiWithdrawApplication(
  token: string,
  appId: string
): Promise<JobApplication> {
  return jobsFetch(`/applications/${appId}/withdraw`, {
    method: "PATCH",
    headers: { Authorization: `Bearer ${token}` },
  });
}
