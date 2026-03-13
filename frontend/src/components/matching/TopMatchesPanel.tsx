"use client";

import { useEffect, useState } from "react";
import Link from "next/link";
import { Loader2, Sparkles, MapPin, Clock } from "lucide-react";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { apiTopProfessionals, type MatchedProfessional } from "@/lib/api/matching";
import { MatchScoreBadge } from "./MatchScoreBadge";
import { AVAILABILITY_LABELS, AVAILABILITY_COLORS } from "@/types/search";

interface TopMatchesPanelProps {
  token: string;
}

export function TopMatchesPanel({ token }: TopMatchesPanelProps) {
  const [matches, setMatches] = useState<MatchedProfessional[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    apiTopProfessionals(token, undefined, 5)
      .then(setMatches)
      .catch(() => setError("Impossibile caricare i match"))
      .finally(() => setLoading(false));
  }, [token]);

  return (
    <Card>
      <CardHeader className="flex flex-row items-center justify-between pb-3">
        <CardTitle className="flex items-center gap-2 text-base">
          <Sparkles className="h-4 w-4 text-indigo-500" />
          I tuoi match
        </CardTitle>
        <Link href="/dashboard/salon/search">
          <Button variant="outline" size="sm" className="text-xs">
            Vedi tutti
          </Button>
        </Link>
      </CardHeader>
      <CardContent>
        {loading ? (
          <div className="flex items-center justify-center py-8">
            <Loader2 className="h-6 w-6 animate-spin text-indigo-500" />
          </div>
        ) : error ? (
          <p className="text-sm text-gray-500">{error}</p>
        ) : matches.length === 0 ? (
          <p className="text-sm text-gray-500">
            Nessun professionista disponibile. Completa il tuo profilo per
            migliorare i match.
          </p>
        ) : (
          <div className="space-y-3">
            {matches.map((m) => (
              <div
                key={m.user_id}
                className="flex items-start gap-3 rounded-lg border p-3 hover:bg-gray-50 transition-colors"
              >
                {/* Avatar placeholder */}
                <div className="flex h-10 w-10 shrink-0 items-center justify-center rounded-full bg-indigo-100 text-sm font-semibold text-indigo-700">
                  {m.first_name[0]}
                  {m.last_name[0]}
                </div>

                <div className="min-w-0 flex-1">
                  <div className="flex flex-wrap items-center gap-2">
                    <span className="font-medium text-gray-900 text-sm">
                      {m.first_name} {m.last_name}
                    </span>
                    <MatchScoreBadge score={m.match_score} size="sm" />
                  </div>

                  <div className="mt-1 flex flex-wrap gap-1">
                    {m.specializations.slice(0, 3).map((s) => (
                      <span
                        key={s}
                        className="rounded-full bg-indigo-50 px-1.5 py-0.5 text-xs text-indigo-600"
                      >
                        {s}
                      </span>
                    ))}
                  </div>

                  <div className="mt-1 flex flex-wrap gap-3 text-xs text-gray-500">
                    {m.preferred_city && (
                      <span className="flex items-center gap-0.5">
                        <MapPin className="h-3 w-3" />
                        {m.preferred_city}
                      </span>
                    )}
                    {m.years_of_experience != null && (
                      <span className="flex items-center gap-0.5">
                        <Clock className="h-3 w-3" />
                        {m.years_of_experience} anni
                      </span>
                    )}
                    <span
                      className={`rounded-full px-1.5 py-0.5 ${
                        AVAILABILITY_COLORS[m.availability_status]
                      }`}
                    >
                      {AVAILABILITY_LABELS[m.availability_status]}
                    </span>
                  </div>
                </div>
              </div>
            ))}
          </div>
        )}
      </CardContent>
    </Card>
  );
}
