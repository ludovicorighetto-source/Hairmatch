"use client";

import { useEffect, useState } from "react";
import Link from "next/link";
import { Loader2, Sparkles, MapPin, Euro } from "lucide-react";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { apiRecommendedJobs, type MatchedJob } from "@/lib/api/matching";
import { MatchScoreBadge } from "./MatchScoreBadge";
import { CONTRACT_TYPE_LABELS, type ContractType } from "@/types/jobs";

interface RecommendedJobsPanelProps {
  token: string;
}

export function RecommendedJobsPanel({ token }: RecommendedJobsPanelProps) {
  const [jobs, setJobs] = useState<MatchedJob[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    apiRecommendedJobs(token, 5)
      .then(setJobs)
      .catch(() => setError("Impossibile caricare i job consigliati"))
      .finally(() => setLoading(false));
  }, [token]);

  return (
    <Card>
      <CardHeader className="flex flex-row items-center justify-between pb-3">
        <CardTitle className="flex items-center gap-2 text-base">
          <Sparkles className="h-4 w-4 text-violet-500" />
          Offerte consigliate
        </CardTitle>
        <Link href="/dashboard/professional/jobs">
          <Button variant="outline" size="sm" className="text-xs">
            Vedi tutte
          </Button>
        </Link>
      </CardHeader>
      <CardContent>
        {loading ? (
          <div className="flex items-center justify-center py-8">
            <Loader2 className="h-6 w-6 animate-spin text-violet-500" />
          </div>
        ) : error ? (
          <p className="text-sm text-gray-500">{error}</p>
        ) : jobs.length === 0 ? (
          <p className="text-sm text-gray-500">
            Nessuna offerta disponibile al momento. Completa il tuo profilo per
            ricevere raccomandazioni più accurate.
          </p>
        ) : (
          <div className="space-y-3">
            {jobs.map((job) => (
              <div
                key={job.id}
                className="rounded-lg border p-3 hover:bg-gray-50 transition-colors"
              >
                <div className="flex flex-wrap items-center gap-2 mb-1">
                  <span className="font-medium text-gray-900 text-sm">
                    {job.title}
                  </span>
                  <MatchScoreBadge score={job.match_score} size="sm" />
                </div>

                <p className="mb-2 line-clamp-1 text-xs text-gray-500">
                  {job.description}
                </p>

                <div className="flex flex-wrap gap-1 mb-2">
                  {job.specializations.slice(0, 3).map((s) => (
                    <span
                      key={s}
                      className="rounded-full bg-violet-50 px-1.5 py-0.5 text-xs text-violet-700"
                    >
                      {s}
                    </span>
                  ))}
                  {job.contract_types.slice(0, 2).map((ct) => (
                    <span
                      key={ct}
                      className="rounded-full bg-gray-100 px-1.5 py-0.5 text-xs text-gray-600"
                    >
                      {CONTRACT_TYPE_LABELS[ct as ContractType] ?? ct}
                    </span>
                  ))}
                </div>

                <div className="flex flex-wrap gap-3 text-xs text-gray-500">
                  {job.city && (
                    <span className="flex items-center gap-0.5">
                      <MapPin className="h-3 w-3" />
                      {job.city}
                      {job.province ? `, ${job.province}` : ""}
                    </span>
                  )}
                  {(job.salary_min || job.salary_max) && (
                    <span className="flex items-center gap-0.5 text-emerald-600">
                      <Euro className="h-3 w-3" />
                      {job.salary_min && job.salary_max
                        ? `${job.salary_min}–${job.salary_max}`
                        : job.salary_min
                        ? `da ${job.salary_min}`
                        : `fino a ${job.salary_max}`}
                    </span>
                  )}
                </div>
              </div>
            ))}
          </div>
        )}
      </CardContent>
    </Card>
  );
}
