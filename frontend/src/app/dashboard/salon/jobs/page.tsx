"use client";

import { useEffect, useState, useCallback } from "react";
import Link from "next/link";
import {
  Plus,
  Briefcase,
  Pencil,
  Trash2,
  ChevronDown,
  ChevronUp,
  Loader2,
  Users,
  X,
  Check,
} from "lucide-react";
import { useAuth } from "@/hooks/useAuth";
import { Button } from "@/components/ui/button";
import {
  Card,
  CardContent,
  CardHeader,
  CardTitle,
  CardDescription,
} from "@/components/ui/card";
import {
  apiListMyJobs,
  apiCreateJobPosting,
  apiUpdateJobPosting,
  apiDeleteJobPosting,
  apiGetJobApplicants,
  apiUpdateApplicationStatus,
} from "@/lib/api/jobs";
import type {
  JobPosting,
  JobApplication,
  CreateJobPostingRequest,
  ContractType,
} from "@/types/jobs";
import {
  CONTRACT_TYPE_LABELS,
  JOB_STATUS_LABELS,
  APPLICATION_STATUS_LABELS,
} from "@/types/jobs";

const SPECIALIZATIONS = [
  "Taglio",
  "Colorazione",
  "Meches",
  "Styling",
  "Trattamenti",
  "Barba",
  "Unghie",
  "Make-up",
];

const CONTRACT_TYPES: ContractType[] = [
  "full_time",
  "part_time",
  "freelance",
  "internship",
];

const STATUS_BADGE: Record<string, string> = {
  open: "bg-green-100 text-green-700",
  draft: "bg-gray-100 text-gray-600",
  closed: "bg-red-100 text-red-700",
};

const APP_STATUS_BADGE: Record<string, string> = {
  pending: "bg-yellow-100 text-yellow-700",
  accepted: "bg-green-100 text-green-700",
  rejected: "bg-red-100 text-red-700",
  withdrawn: "bg-gray-100 text-gray-500",
};

interface JobFormData {
  title: string;
  description: string;
  specializations: string[];
  contract_types: string[];
  city: string;
  province: string;
  salary_min: string;
  salary_max: string;
  status: "draft" | "open";
}

const emptyForm = (): JobFormData => ({
  title: "",
  description: "",
  specializations: [],
  contract_types: [],
  city: "",
  province: "",
  salary_min: "",
  salary_max: "",
  status: "open",
});

function toggle<T>(arr: T[], item: T): T[] {
  return arr.includes(item) ? arr.filter((x) => x !== item) : [...arr, item];
}

export default function SalonJobsPage() {
  const { user, accessToken } = useAuth();

  const [jobs, setJobs] = useState<JobPosting[]>([]);
  const [total, setTotal] = useState(0);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  // Form state
  const [showForm, setShowForm] = useState(false);
  const [editingJob, setEditingJob] = useState<JobPosting | null>(null);
  const [form, setForm] = useState<JobFormData>(emptyForm());
  const [saving, setSaving] = useState(false);
  const [formError, setFormError] = useState<string | null>(null);

  // Applicants panel
  const [expandedJob, setExpandedJob] = useState<string | null>(null);
  const [applicants, setApplicants] = useState<Record<string, JobApplication[]>>({});
  const [loadingApplicants, setLoadingApplicants] = useState<string | null>(null);

  const loadJobs = useCallback(async () => {
    if (!accessToken) return;
    setLoading(true);
    try {
      const res = await apiListMyJobs(accessToken);
      setJobs(res.items);
      setTotal(res.total);
    } catch {
      setError("Errore nel caricamento degli annunci.");
    } finally {
      setLoading(false);
    }
  }, [accessToken]);

  useEffect(() => {
    loadJobs();
  }, [loadJobs]);

  const openCreateForm = () => {
    setEditingJob(null);
    setForm(emptyForm());
    setFormError(null);
    setShowForm(true);
  };

  const openEditForm = (job: JobPosting) => {
    setEditingJob(job);
    setForm({
      title: job.title,
      description: job.description,
      specializations: job.specializations,
      contract_types: job.contract_types,
      city: job.city ?? "",
      province: job.province ?? "",
      salary_min: job.salary_min != null ? String(job.salary_min) : "",
      salary_max: job.salary_max != null ? String(job.salary_max) : "",
      status: job.status === "closed" ? "open" : job.status,
    });
    setFormError(null);
    setShowForm(true);
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!accessToken) return;
    setSaving(true);
    setFormError(null);
    try {
      const payload: CreateJobPostingRequest = {
        title: form.title,
        description: form.description,
        specializations: form.specializations,
        contract_types: form.contract_types,
        city: form.city || undefined,
        province: form.province || undefined,
        salary_min: form.salary_min ? Number(form.salary_min) : undefined,
        salary_max: form.salary_max ? Number(form.salary_max) : undefined,
        status: form.status,
      };
      if (editingJob) {
        await apiUpdateJobPosting(accessToken, editingJob.id, payload);
      } else {
        await apiCreateJobPosting(accessToken, payload);
      }
      setShowForm(false);
      await loadJobs();
    } catch (err) {
      setFormError(err instanceof Error ? err.message : "Errore nel salvataggio.");
    } finally {
      setSaving(false);
    }
  };

  const handleDelete = async (jobId: string) => {
    if (!accessToken) return;
    if (!confirm("Eliminare questo annuncio?")) return;
    try {
      await apiDeleteJobPosting(accessToken, jobId);
      await loadJobs();
    } catch {
      alert("Errore nell'eliminazione.");
    }
  };

  const toggleApplicants = async (jobId: string) => {
    if (expandedJob === jobId) {
      setExpandedJob(null);
      return;
    }
    setExpandedJob(jobId);
    if (applicants[jobId]) return;
    if (!accessToken) return;
    setLoadingApplicants(jobId);
    try {
      const apps = await apiGetJobApplicants(accessToken, jobId);
      setApplicants((prev) => ({ ...prev, [jobId]: apps }));
    } catch {
      // silent
    } finally {
      setLoadingApplicants(null);
    }
  };

  const handleAppStatus = async (
    jobId: string,
    appId: string,
    status: string
  ) => {
    if (!accessToken) return;
    try {
      const updated = await apiUpdateApplicationStatus(accessToken, appId, status);
      setApplicants((prev) => ({
        ...prev,
        [jobId]: prev[jobId].map((a) => (a.id === appId ? updated : a)),
      }));
    } catch {
      alert("Errore nell'aggiornamento.");
    }
  };

  if (!user) {
    return (
      <div className="flex items-center justify-center py-20">
        <Loader2 className="h-8 w-8 animate-spin text-indigo-600" />
      </div>
    );
  }

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold text-gray-900">I miei annunci</h1>
          <p className="text-sm text-gray-500">
            {total} annunci totali
          </p>
        </div>
        <Button
          onClick={openCreateForm}
          className="bg-indigo-600 hover:bg-indigo-700 flex items-center gap-2"
        >
          <Plus className="h-4 w-4" />
          Nuovo annuncio
        </Button>
      </div>

      {/* Create/Edit Form */}
      {showForm && (
        <Card className="border-indigo-200">
          <CardHeader>
            <CardTitle className="text-lg">
              {editingJob ? "Modifica annuncio" : "Crea nuovo annuncio"}
            </CardTitle>
          </CardHeader>
          <CardContent>
            <form onSubmit={handleSubmit} className="space-y-4">
              {formError && (
                <div className="rounded-md bg-red-50 p-3 text-sm text-red-700">
                  {formError}
                </div>
              )}

              <div>
                <label className="mb-1 block text-sm font-medium text-gray-700">
                  Titolo *
                </label>
                <input
                  type="text"
                  required
                  value={form.title}
                  onChange={(e) => setForm({ ...form, title: e.target.value })}
                  className="w-full rounded-md border border-gray-300 px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-indigo-500"
                  placeholder="Es. Cerca colorista esperto"
                />
              </div>

              <div>
                <label className="mb-1 block text-sm font-medium text-gray-700">
                  Descrizione *
                </label>
                <textarea
                  required
                  rows={4}
                  value={form.description}
                  onChange={(e) =>
                    setForm({ ...form, description: e.target.value })
                  }
                  className="w-full rounded-md border border-gray-300 px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-indigo-500"
                  placeholder="Descrivi la posizione, i requisiti e cosa offri..."
                />
              </div>

              <div>
                <label className="mb-2 block text-sm font-medium text-gray-700">
                  Specializzazioni
                </label>
                <div className="flex flex-wrap gap-2">
                  {SPECIALIZATIONS.map((s) => (
                    <button
                      key={s}
                      type="button"
                      onClick={() =>
                        setForm({
                          ...form,
                          specializations: toggle(form.specializations, s),
                        })
                      }
                      className={`rounded-full px-3 py-1 text-xs font-medium transition-colors ${
                        form.specializations.includes(s)
                          ? "bg-indigo-600 text-white"
                          : "bg-gray-100 text-gray-700 hover:bg-gray-200"
                      }`}
                    >
                      {s}
                    </button>
                  ))}
                </div>
              </div>

              <div>
                <label className="mb-2 block text-sm font-medium text-gray-700">
                  Tipo contratto
                </label>
                <div className="flex flex-wrap gap-2">
                  {CONTRACT_TYPES.map((ct) => (
                    <button
                      key={ct}
                      type="button"
                      onClick={() =>
                        setForm({
                          ...form,
                          contract_types: toggle(form.contract_types, ct),
                        })
                      }
                      className={`rounded-full px-3 py-1 text-xs font-medium transition-colors ${
                        form.contract_types.includes(ct)
                          ? "bg-indigo-600 text-white"
                          : "bg-gray-100 text-gray-700 hover:bg-gray-200"
                      }`}
                    >
                      {CONTRACT_TYPE_LABELS[ct]}
                    </button>
                  ))}
                </div>
              </div>

              <div className="grid grid-cols-2 gap-4">
                <div>
                  <label className="mb-1 block text-sm font-medium text-gray-700">
                    Città
                  </label>
                  <input
                    type="text"
                    value={form.city}
                    onChange={(e) => setForm({ ...form, city: e.target.value })}
                    className="w-full rounded-md border border-gray-300 px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-indigo-500"
                    placeholder="Es. Milano"
                  />
                </div>
                <div>
                  <label className="mb-1 block text-sm font-medium text-gray-700">
                    Provincia
                  </label>
                  <input
                    type="text"
                    maxLength={2}
                    value={form.province}
                    onChange={(e) =>
                      setForm({
                        ...form,
                        province: e.target.value.toUpperCase(),
                      })
                    }
                    className="w-full rounded-md border border-gray-300 px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-indigo-500"
                    placeholder="MI"
                  />
                </div>
              </div>

              <div className="grid grid-cols-2 gap-4">
                <div>
                  <label className="mb-1 block text-sm font-medium text-gray-700">
                    RAL minima (€)
                  </label>
                  <input
                    type="number"
                    min={0}
                    value={form.salary_min}
                    onChange={(e) =>
                      setForm({ ...form, salary_min: e.target.value })
                    }
                    className="w-full rounded-md border border-gray-300 px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-indigo-500"
                    placeholder="20000"
                  />
                </div>
                <div>
                  <label className="mb-1 block text-sm font-medium text-gray-700">
                    RAL massima (€)
                  </label>
                  <input
                    type="number"
                    min={0}
                    value={form.salary_max}
                    onChange={(e) =>
                      setForm({ ...form, salary_max: e.target.value })
                    }
                    className="w-full rounded-md border border-gray-300 px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-indigo-500"
                    placeholder="35000"
                  />
                </div>
              </div>

              <div>
                <label className="mb-1 block text-sm font-medium text-gray-700">
                  Stato
                </label>
                <select
                  value={form.status}
                  onChange={(e) =>
                    setForm({
                      ...form,
                      status: e.target.value as "draft" | "open",
                    })
                  }
                  className="w-full rounded-md border border-gray-300 px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-indigo-500"
                >
                  <option value="open">Aperto (visibile pubblicamente)</option>
                  <option value="draft">Bozza (nascosto)</option>
                </select>
              </div>

              <div className="flex justify-end gap-3 pt-2">
                <Button
                  type="button"
                  variant="outline"
                  onClick={() => setShowForm(false)}
                >
                  Annulla
                </Button>
                <Button
                  type="submit"
                  disabled={saving}
                  className="bg-indigo-600 hover:bg-indigo-700"
                >
                  {saving ? (
                    <Loader2 className="h-4 w-4 animate-spin" />
                  ) : editingJob ? (
                    "Salva modifiche"
                  ) : (
                    "Pubblica annuncio"
                  )}
                </Button>
              </div>
            </form>
          </CardContent>
        </Card>
      )}

      {/* Job list */}
      {loading ? (
        <div className="flex items-center justify-center py-16">
          <Loader2 className="h-8 w-8 animate-spin text-indigo-600" />
        </div>
      ) : error ? (
        <div className="rounded-md bg-red-50 p-4 text-sm text-red-700">
          {error}
        </div>
      ) : jobs.length === 0 ? (
        <Card className="border-dashed">
          <CardContent className="flex flex-col items-center justify-center py-16 text-center">
            <Briefcase className="mb-4 h-12 w-12 text-gray-300" />
            <h3 className="mb-1 font-medium text-gray-700">
              Nessun annuncio ancora
            </h3>
            <p className="mb-4 text-sm text-gray-500">
              Crea il tuo primo annuncio per iniziare a ricevere candidature.
            </p>
            <Button
              onClick={openCreateForm}
              className="bg-indigo-600 hover:bg-indigo-700"
            >
              Crea il primo annuncio
            </Button>
          </CardContent>
        </Card>
      ) : (
        <div className="space-y-4">
          {jobs.map((job) => (
            <Card key={job.id}>
              <CardContent className="p-5">
                <div className="flex items-start justify-between gap-4">
                  <div className="min-w-0 flex-1">
                    <div className="mb-1 flex flex-wrap items-center gap-2">
                      <h3 className="font-semibold text-gray-900 truncate">
                        {job.title}
                      </h3>
                      <span
                        className={`inline-flex items-center rounded-full px-2 py-0.5 text-xs font-medium ${
                          STATUS_BADGE[job.status] || "bg-gray-100 text-gray-600"
                        }`}
                      >
                        {JOB_STATUS_LABELS[job.status]}
                      </span>
                    </div>

                    <p className="mb-3 line-clamp-2 text-sm text-gray-600">
                      {job.description}
                    </p>

                    <div className="flex flex-wrap gap-1.5">
                      {job.specializations.map((s) => (
                        <span
                          key={s}
                          className="rounded-full bg-indigo-50 px-2 py-0.5 text-xs text-indigo-700"
                        >
                          {s}
                        </span>
                      ))}
                      {job.contract_types.map((ct) => (
                        <span
                          key={ct}
                          className="rounded-full bg-gray-100 px-2 py-0.5 text-xs text-gray-600"
                        >
                          {CONTRACT_TYPE_LABELS[ct as ContractType] ?? ct}
                        </span>
                      ))}
                      {job.city && (
                        <span className="rounded-full bg-gray-100 px-2 py-0.5 text-xs text-gray-600">
                          {job.city}
                          {job.province ? `, ${job.province}` : ""}
                        </span>
                      )}
                      {(job.salary_min || job.salary_max) && (
                        <span className="rounded-full bg-emerald-50 px-2 py-0.5 text-xs text-emerald-700">
                          {job.salary_min && job.salary_max
                            ? `€${job.salary_min}–${job.salary_max}`
                            : job.salary_min
                            ? `da €${job.salary_min}`
                            : `fino a €${job.salary_max}`}
                        </span>
                      )}
                    </div>
                  </div>

                  <div className="flex shrink-0 items-center gap-2">
                    <Button
                      size="sm"
                      variant="outline"
                      onClick={() => toggleApplicants(job.id)}
                      className="flex items-center gap-1 text-xs"
                    >
                      <Users className="h-3.5 w-3.5" />
                      Candidati
                      {expandedJob === job.id ? (
                        <ChevronUp className="h-3.5 w-3.5" />
                      ) : (
                        <ChevronDown className="h-3.5 w-3.5" />
                      )}
                    </Button>
                    <Button
                      size="sm"
                      variant="outline"
                      onClick={() => openEditForm(job)}
                    >
                      <Pencil className="h-3.5 w-3.5" />
                    </Button>
                    <Button
                      size="sm"
                      variant="outline"
                      onClick={() => handleDelete(job.id)}
                      className="text-red-600 hover:bg-red-50 hover:text-red-700"
                    >
                      <Trash2 className="h-3.5 w-3.5" />
                    </Button>
                  </div>
                </div>

                {/* Applicants section */}
                {expandedJob === job.id && (
                  <div className="mt-4 border-t pt-4">
                    {loadingApplicants === job.id ? (
                      <div className="flex items-center gap-2 text-sm text-gray-500">
                        <Loader2 className="h-4 w-4 animate-spin" />
                        Caricamento candidature...
                      </div>
                    ) : !applicants[job.id]?.length ? (
                      <p className="text-sm text-gray-500">
                        Nessuna candidatura ricevuta.
                      </p>
                    ) : (
                      <div className="space-y-3">
                        <p className="text-xs font-medium uppercase tracking-wide text-gray-500">
                          {applicants[job.id].length} candidature
                        </p>
                        {applicants[job.id].map((app) => (
                          <div
                            key={app.id}
                            className="flex items-start justify-between rounded-md bg-gray-50 p-3"
                          >
                            <div className="min-w-0 flex-1">
                              <div className="mb-1 flex items-center gap-2">
                                <span className="text-xs font-mono text-gray-500 truncate">
                                  ID: {app.professional_id.slice(0, 8)}…
                                </span>
                                <span
                                  className={`rounded-full px-2 py-0.5 text-xs font-medium ${
                                    APP_STATUS_BADGE[app.status] ||
                                    "bg-gray-100 text-gray-600"
                                  }`}
                                >
                                  {APPLICATION_STATUS_LABELS[app.status]}
                                </span>
                              </div>
                              {app.cover_letter && (
                                <p className="line-clamp-2 text-sm text-gray-700">
                                  {app.cover_letter}
                                </p>
                              )}
                              <p className="mt-1 text-xs text-gray-400">
                                {new Date(app.created_at).toLocaleDateString(
                                  "it-IT"
                                )}
                              </p>
                            </div>
                            {app.status === "pending" && (
                              <div className="ml-3 flex shrink-0 gap-2">
                                <button
                                  onClick={() =>
                                    handleAppStatus(job.id, app.id, "accepted")
                                  }
                                  className="flex items-center gap-1 rounded-md bg-green-100 px-2 py-1 text-xs font-medium text-green-700 hover:bg-green-200"
                                >
                                  <Check className="h-3 w-3" />
                                  Accetta
                                </button>
                                <button
                                  onClick={() =>
                                    handleAppStatus(job.id, app.id, "rejected")
                                  }
                                  className="flex items-center gap-1 rounded-md bg-red-100 px-2 py-1 text-xs font-medium text-red-700 hover:bg-red-200"
                                >
                                  <X className="h-3 w-3" />
                                  Rifiuta
                                </button>
                              </div>
                            )}
                          </div>
                        ))}
                      </div>
                    )}
                  </div>
                )}
              </CardContent>
            </Card>
          ))}
        </div>
      )}
    </div>
  );
}
