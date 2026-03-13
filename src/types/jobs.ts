export type JobStatus = "draft" | "open" | "closed";
export type ApplicationStatus = "pending" | "accepted" | "rejected" | "withdrawn";

export type ContractType = "full_time" | "part_time" | "freelance" | "internship";

export const CONTRACT_TYPE_LABELS: Record<ContractType, string> = {
  full_time: "Tempo pieno",
  part_time: "Part-time",
  freelance: "Freelance",
  internship: "Stage",
};

export const JOB_STATUS_LABELS: Record<JobStatus, string> = {
  draft: "Bozza",
  open: "Aperto",
  closed: "Chiuso",
};

export const APPLICATION_STATUS_LABELS: Record<ApplicationStatus, string> = {
  pending: "In attesa",
  accepted: "Accettata",
  rejected: "Rifiutata",
  withdrawn: "Ritirata",
};

export interface JobPosting {
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
  expires_at: string | null;
  created_at: string;
  updated_at: string;
}

export interface JobPostingListResponse {
  items: JobPosting[];
  total: number;
  page: number;
  limit: number;
  pages: number;
}

export interface CreateJobPostingRequest {
  title: string;
  description: string;
  specializations: string[];
  contract_types: string[];
  city?: string;
  province?: string;
  salary_min?: number;
  salary_max?: number;
  status?: JobStatus;
  expires_at?: string;
}

export interface UpdateJobPostingRequest {
  title?: string;
  description?: string;
  specializations?: string[];
  contract_types?: string[];
  city?: string;
  province?: string;
  salary_min?: number;
  salary_max?: number;
  status?: JobStatus;
  expires_at?: string;
}

export interface JobApplication {
  id: string;
  job_id: string;
  professional_id: string;
  cover_letter: string | null;
  status: ApplicationStatus;
  created_at: string;
  updated_at: string;
}

export interface ApplicationWithJob extends JobApplication {
  job: JobPosting;
}
