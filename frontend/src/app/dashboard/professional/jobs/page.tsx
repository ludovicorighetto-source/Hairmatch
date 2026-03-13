"use client";

import { useEffect, useState, useCallback } from "react";
import {
  Briefcase,
  MapPin,
  Euro,
  Clock,
  Loader2,
  Send,
  CheckCircle,
  X,
} from "lucide-react";
import { useAuth } from "@/hooks/useAuth";
import { Button } from "@/components/ui/button";
import {
  Card,
  CardContent,
  CardHeader,
  CardTitle,
} from "@/components/ui/card";
import {
  apiBrowseJobs,
  apiApplyToJob,
  apiMyApplications,
  apiWithdrawApplication,
} from "@/lib/api/jobs";
import type { JobPosting, ApplicationWithJob, ContractType } from "@/types/jobs";
import {
  CONTRACT_TYPE_LABELS,
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

const APP_STATUS_BADGE: Record<string, string> = {
  pending: "bg-yellow-100 text-yellow-700",
  accepted: "bg-green-100 text-green-700",
  rejected: "bg-red-100 text-red-700",
  withdrawn: "bg-gray-100 text-gray-500",
};

function toggle<T>(arr: T[], item: T): T[] {
  return arr.includes(item) ? arr.filter((x) => x !== item) : [...arr, item];
}

export default function ProfessionalJobsPage() {
  const { user, accessToken } = useAuth();

  const [tab, setTab] = useState<"browse" | "applications">("browse");

  // Browse state
  const [jobs, setJobs] = useState<JobPosting[]>([]);
  const [total, setTotal] = useState(0);
  const [page, setPage] = useState(1);
  const [loadingJobs, setLoadingJobs] = useState(false);

  // Filters
  const [city, setCity] = useState("");
  const [province, setProvince] = useState("");
  const [selectedSpecs, setSelectedSpecs] = useState<string[]>([]);
  const [selectedContracts, setSelectedContracts] = useState<string[]>([]);

  // Applications state
  const [applications, setApplications] = useState<ApplicationWithJob[]>([]);
  const [loadingApps, setLoadingApps] = useState(false);

  // Apply modal
  const [applyJob, setApplyJob] = useState<JobPosting | null>(null);
  const [coverLetter, setCoverLetter] = useState("");
  const [applying, setApplying] = useState(false);
  const [applyError, setApplyError] = useState<string | null>(null);

  // Set of already-applied job ids
  const appliedJobIds = new Set(applications.map((a) => a.job_id));

  const loadJobs = useCallback(async () => {
    setLoadingJobs(true);
    try {
      const res = await apiBrowseJobs({
        city: city || undefined,
        province: province || undefined,
        specializations: selectedSpecs.length ? selectedSpecs : undefined,
        contract_types: selectedContracts.length ? selectedContracts : undefined,
        page,
        limit: 12,
      });
      setJobs(res.items);
      setTotal(res.total);
    } catch {
      // silent
    } finally {
      setLoadingJobs(false);
    }
  }, [city, province, selectedSpecs, selectedContracts, page]);

  const loadApplications = useCallback(async () => {
    if (!accessToken) return;
    setLoadingApps(true);
    try {
      const apps = await apiMyApplications(accessToken);
      setApplications(apps);
    } catch {
      // silent
    } finally {
      setLoadingApps(false);
    }
  }, [accessToken]);

  useEffect(() => {
    loadJobs();
  }, [loadJobs]);

  useEffect(() => {
    if (tab === "applications") loadApplications();
  }, [tab, loadApplications]);

  const handleSearch = (e: React.FormEvent) => {
    e.preventDefault();
    setPage(1);
    loadJobs();
  };

  const openApplyModal = (job: JobPosting) => {
    setApplyJob(job);
    setCoverLetter("");
    setApplyError(null);
  };

  const handleApply = async () => {
    if (!accessToken || !applyJob) return;
    setApplying(true);
    setApplyError(null);
    try {
      await apiApplyToJob(accessToken, applyJob.id, coverLetter || undefined);
      setApplyJob(null);
      await loadApplications();
    } catch (err) {
      setApplyError(
        err instanceof Error ? err.message : "Errore nell'invio della candidatura."
      );
    } finally {
      setApplying(false);
    }
  };

  const handleWithdraw = async (appId: string) => {
    if (!accessToken) return;
    if (!confirm("Ritirare questa candidatura?")) return;
    try {
      await apiWithdrawApplication(accessToken, appId);
      await loadApplications();
    } catch {
      alert("Errore nel ritiro.");
    }
  };

  if (!user) {
    return (
      <div className="flex items-center justify-center py-20">
        <Loader2 className="h-8 w-8 animate-spin text-violet-600" />
      </div>
    );
  }

  return (
    <div className="space-y-6">
      {/* Header */}
      <div>
        <h1 className="text-2xl font-bold text-gray-900">Offerte di lavoro</h1>
        <p className="text-sm text-gray-500">
          Scopri le posizioni aperte nei saloni in tutta Italia.
        </p>
      </div>

      {/* Tabs */}
      <div className="flex gap-1 rounded-lg bg-gray-100 p-1 w-fit">
        <button
          onClick={() => setTab("browse")}
          className={`rounded-md px-4 py-1.5 text-sm font-medium transition-colors ${
            tab === "browse"
              ? "bg-white text-gray-900 shadow-sm"
              : "text-gray-500 hover:text-gray-700"
          }`}
        >
          Cerca offerte
        </button>
        <button
          onClick={() => setTab("applications")}
          className={`rounded-md px-4 py-1.5 text-sm font-medium transition-colors ${
            tab === "applications"
              ? "bg-white text-gray-900 shadow-sm"
              : "text-gray-500 hover:text-gray-700"
          }`}
        >
          Le mie candidature
          {applications.length > 0 && (
            <span className="ml-1.5 rounded-full bg-violet-600 px-1.5 py-0.5 text-xs text-white">
              {applications.length}
            </span>
          )}
        </button>
      </div>

      {tab === "browse" ? (
        <>
          {/* Filters */}
          <Card>
            <CardContent className="pt-5">
              <form onSubmit={handleSearch} className="space-y-4">
                <div className="grid grid-cols-1 gap-4 sm:grid-cols-2">
                  <div>
                    <label className="mb-1 block text-sm font-medium text-gray-700">
                      Città
                    </label>
                    <input
                      type="text"
                      value={city}
                      onChange={(e) => setCity(e.target.value)}
                      className="w-full rounded-md border border-gray-300 px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-violet-500"
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
                      value={province}
                      onChange={(e) =>
                        setProvince(e.target.value.toUpperCase())
                      }
                      className="w-full rounded-md border border-gray-300 px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-violet-500"
                      placeholder="MI"
                    />
                  </div>
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
                          setSelectedSpecs(toggle(selectedSpecs, s))
                        }
                        className={`rounded-full px-3 py-1 text-xs font-medium transition-colors ${
                          selectedSpecs.includes(s)
                            ? "bg-violet-600 text-white"
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
                          setSelectedContracts(toggle(selectedContracts, ct))
                        }
                        className={`rounded-full px-3 py-1 text-xs font-medium transition-colors ${
                          selectedContracts.includes(ct)
                            ? "bg-violet-600 text-white"
                            : "bg-gray-100 text-gray-700 hover:bg-gray-200"
                        }`}
                      >
                        {CONTRACT_TYPE_LABELS[ct]}
                      </button>
                    ))}
                  </div>
                </div>

                <Button
                  type="submit"
                  className="bg-violet-600 hover:bg-violet-700"
                >
                  Cerca
                </Button>
              </form>
            </CardContent>
          </Card>

          {/* Results */}
          {loadingJobs ? (
            <div className="flex items-center justify-center py-16">
              <Loader2 className="h-8 w-8 animate-spin text-violet-600" />
            </div>
          ) : jobs.length === 0 ? (
            <Card className="border-dashed">
              <CardContent className="flex flex-col items-center justify-center py-16 text-center">
                <Briefcase className="mb-4 h-12 w-12 text-gray-300" />
                <h3 className="mb-1 font-medium text-gray-700">
                  Nessuna offerta trovata
                </h3>
                <p className="text-sm text-gray-500">
                  Prova a modificare i filtri di ricerca.
                </p>
              </CardContent>
            </Card>
          ) : (
            <>
              <p className="text-sm text-gray-500">{total} offerte trovate</p>
              <div className="grid gap-4 sm:grid-cols-2">
                {jobs.map((job) => {
                  const alreadyApplied = appliedJobIds.has(job.id);
                  return (
                    <Card
                      key={job.id}
                      className={alreadyApplied ? "opacity-75" : ""}
                    >
                      <CardContent className="p-5">
                        <div className="mb-3">
                          <h3 className="font-semibold text-gray-900">
                            {job.title}
                          </h3>
                          <p className="mt-1 line-clamp-2 text-sm text-gray-600">
                            {job.description}
                          </p>
                        </div>

                        <div className="mb-4 flex flex-wrap gap-1.5">
                          {job.specializations.map((s) => (
                            <span
                              key={s}
                              className="rounded-full bg-violet-50 px-2 py-0.5 text-xs text-violet-700"
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
                        </div>

                        <div className="mb-4 flex flex-wrap gap-3 text-xs text-gray-500">
                          {job.city && (
                            <span className="flex items-center gap-1">
                              <MapPin className="h-3.5 w-3.5" />
                              {job.city}
                              {job.province ? `, ${job.province}` : ""}
                            </span>
                          )}
                          {(job.salary_min || job.salary_max) && (
                            <span className="flex items-center gap-1 text-emerald-600">
                              <Euro className="h-3.5 w-3.5" />
                              {job.salary_min && job.salary_max
                                ? `${job.salary_min}–${job.salary_max}`
                                : job.salary_min
                                ? `da ${job.salary_min}`
                                : `fino a ${job.salary_max}`}
                            </span>
                          )}
                          <span className="flex items-center gap-1">
                            <Clock className="h-3.5 w-3.5" />
                            {new Date(job.created_at).toLocaleDateString(
                              "it-IT"
                            )}
                          </span>
                        </div>

                        {alreadyApplied ? (
                          <div className="flex items-center gap-1.5 text-sm text-green-600">
                            <CheckCircle className="h-4 w-4" />
                            Candidatura inviata
                          </div>
                        ) : (
                          <Button
                            size="sm"
                            onClick={() => openApplyModal(job)}
                            className="bg-violet-600 hover:bg-violet-700 flex items-center gap-1.5"
                          >
                            <Send className="h-3.5 w-3.5" />
                            Candidati
                          </Button>
                        )}
                      </CardContent>
                    </Card>
                  );
                })}
              </div>

              {/* Pagination */}
              {total > 12 && (
                <div className="flex items-center justify-center gap-2">
                  <Button
                    variant="outline"
                    size="sm"
                    disabled={page <= 1}
                    onClick={() => setPage((p) => p - 1)}
                  >
                    Precedente
                  </Button>
                  <span className="text-sm text-gray-600">
                    Pagina {page} di {Math.ceil(total / 12)}
                  </span>
                  <Button
                    variant="outline"
                    size="sm"
                    disabled={page >= Math.ceil(total / 12)}
                    onClick={() => setPage((p) => p + 1)}
                  >
                    Successiva
                  </Button>
                </div>
              )}
            </>
          )}
        </>
      ) : (
        /* Applications tab */
        <div className="space-y-4">
          {loadingApps ? (
            <div className="flex items-center justify-center py-16">
              <Loader2 className="h-8 w-8 animate-spin text-violet-600" />
            </div>
          ) : applications.length === 0 ? (
            <Card className="border-dashed">
              <CardContent className="flex flex-col items-center justify-center py-16 text-center">
                <Briefcase className="mb-4 h-12 w-12 text-gray-300" />
                <h3 className="mb-1 font-medium text-gray-700">
                  Nessuna candidatura ancora
                </h3>
                <p className="mb-4 text-sm text-gray-500">
                  Sfoglia le offerte e invia la tua prima candidatura.
                </p>
                <Button
                  onClick={() => setTab("browse")}
                  className="bg-violet-600 hover:bg-violet-700"
                >
                  Cerca offerte
                </Button>
              </CardContent>
            </Card>
          ) : (
            applications.map((app) => (
              <Card key={app.id}>
                <CardContent className="p-5">
                  <div className="flex items-start justify-between gap-4">
                    <div className="min-w-0 flex-1">
                      <div className="mb-1 flex flex-wrap items-center gap-2">
                        <h3 className="font-semibold text-gray-900">
                          {app.job.title}
                        </h3>
                        <span
                          className={`rounded-full px-2 py-0.5 text-xs font-medium ${
                            APP_STATUS_BADGE[app.status] ||
                            "bg-gray-100 text-gray-600"
                          }`}
                        >
                          {APPLICATION_STATUS_LABELS[app.status]}
                        </span>
                      </div>

                      <p className="mb-2 line-clamp-2 text-sm text-gray-600">
                        {app.job.description}
                      </p>

                      <div className="flex flex-wrap gap-1.5">
                        {app.job.specializations.map((s) => (
                          <span
                            key={s}
                            className="rounded-full bg-violet-50 px-2 py-0.5 text-xs text-violet-700"
                          >
                            {s}
                          </span>
                        ))}
                        {app.job.city && (
                          <span className="flex items-center gap-1 text-xs text-gray-500">
                            <MapPin className="h-3 w-3" />
                            {app.job.city}
                          </span>
                        )}
                      </div>

                      {app.cover_letter && (
                        <p className="mt-2 text-sm text-gray-500 italic">
                          &ldquo;{app.cover_letter}&rdquo;
                        </p>
                      )}

                      <p className="mt-2 text-xs text-gray-400">
                        Inviata il{" "}
                        {new Date(app.created_at).toLocaleDateString("it-IT")}
                      </p>
                    </div>

                    {app.status === "pending" && (
                      <Button
                        size="sm"
                        variant="outline"
                        onClick={() => handleWithdraw(app.id)}
                        className="shrink-0 text-red-600 hover:bg-red-50 hover:text-red-700"
                      >
                        <X className="h-3.5 w-3.5 mr-1" />
                        Ritira
                      </Button>
                    )}
                  </div>
                </CardContent>
              </Card>
            ))
          )}
        </div>
      )}

      {/* Apply modal */}
      {applyJob && (
        <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/50 p-4">
          <Card className="w-full max-w-md">
            <CardHeader>
              <CardTitle className="text-lg">
                Candidatura per: {applyJob.title}
              </CardTitle>
            </CardHeader>
            <CardContent className="space-y-4">
              {applyError && (
                <div className="rounded-md bg-red-50 p-3 text-sm text-red-700">
                  {applyError}
                </div>
              )}
              <div>
                <label className="mb-1 block text-sm font-medium text-gray-700">
                  Lettera di presentazione (opzionale)
                </label>
                <textarea
                  rows={4}
                  value={coverLetter}
                  onChange={(e) => setCoverLetter(e.target.value)}
                  maxLength={3000}
                  className="w-full rounded-md border border-gray-300 px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-violet-500"
                  placeholder="Racconta brevemente perché sei la persona giusta per questo ruolo..."
                />
                <p className="mt-1 text-right text-xs text-gray-400">
                  {coverLetter.length}/3000
                </p>
              </div>
              <div className="flex justify-end gap-3">
                <Button
                  variant="outline"
                  onClick={() => setApplyJob(null)}
                  disabled={applying}
                >
                  Annulla
                </Button>
                <Button
                  onClick={handleApply}
                  disabled={applying}
                  className="bg-violet-600 hover:bg-violet-700"
                >
                  {applying ? (
                    <Loader2 className="h-4 w-4 animate-spin" />
                  ) : (
                    <>
                      <Send className="mr-1.5 h-3.5 w-3.5" />
                      Invia candidatura
                    </>
                  )}
                </Button>
              </div>
            </CardContent>
          </Card>
        </div>
      )}
    </div>
  );
}
