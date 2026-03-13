"use client";

import { useState, useCallback } from "react";
import Link from "next/link";
import { ArrowLeft, Search, Star, MapPin, Briefcase, Loader2 } from "lucide-react";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Card, CardContent } from "@/components/ui/card";
import { Alert, AlertDescription } from "@/components/ui/alert";
import { apiSearchProfessionals } from "@/lib/api/search";
import type { ProfessionalCard, PaginatedResult } from "@/types/search";
import { AVAILABILITY_LABELS, AVAILABILITY_COLORS } from "@/types/search";
import { SPECIALIZATIONS, ITALIAN_PROVINCES } from "@/types/auth";

export default function SalonSearchPage() {
  const [city, setCity] = useState("");
  const [province, setProvince] = useState("");
  const [selectedSpecs, setSelectedSpecs] = useState<string[]>([]);
  const [results, setResults] = useState<PaginatedResult<ProfessionalCard> | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [page, setPage] = useState(1);

  const toggleSpec = (spec: string) => {
    setSelectedSpecs((prev) =>
      prev.includes(spec) ? prev.filter((s) => s !== spec) : [...prev, spec]
    );
  };

  const handleSearch = useCallback(
    async (searchPage = 1) => {
      setLoading(true);
      setError(null);
      setPage(searchPage);
      try {
        const data = await apiSearchProfessionals({
          city: city || undefined,
          province: province || undefined,
          specializations: selectedSpecs.length > 0 ? selectedSpecs : undefined,
          page: searchPage,
          limit: 12,
        });
        setResults(data);
      } catch (err) {
        setError("Errore nella ricerca. Riprova.");
      } finally {
        setLoading(false);
      }
    },
    [city, province, selectedSpecs]
  );

  return (
    <div className="space-y-6">
      <div className="flex items-center gap-4">
        <Link href="/dashboard/salon">
          <Button variant="ghost" size="sm" className="flex items-center gap-2">
            <ArrowLeft className="h-4 w-4" />
            Dashboard
          </Button>
        </Link>
        <div>
          <h1 className="text-2xl font-bold text-gray-900">Cerca Professionisti</h1>
          <p className="text-sm text-gray-500">Trova il professionista ideale per il tuo salone</p>
        </div>
      </div>

      {/* Filters */}
      <Card>
        <CardContent className="pt-6 space-y-4">
          <div className="grid gap-4 sm:grid-cols-2">
            <div className="space-y-1">
              <Label htmlFor="city">Città</Label>
              <Input
                id="city"
                placeholder="es. Milano"
                value={city}
                onChange={(e) => setCity(e.target.value)}
              />
            </div>
            <div className="space-y-1">
              <Label htmlFor="province">Provincia</Label>
              <select
                id="province"
                value={province}
                onChange={(e) => setProvince(e.target.value)}
                className="w-full rounded-md border border-input bg-transparent px-3 py-2 text-sm shadow-sm focus:outline-none focus:ring-1 focus:ring-ring"
              >
                <option value="">Tutte le province</option>
                {ITALIAN_PROVINCES.map((p) => (
                  <option key={p} value={p}>{p}</option>
                ))}
              </select>
            </div>
          </div>

          <div className="space-y-2">
            <Label>Specializzazioni</Label>
            <div className="flex flex-wrap gap-2">
              {SPECIALIZATIONS.map((spec) => {
                const selected = selectedSpecs.includes(spec);
                return (
                  <button
                    key={spec}
                    type="button"
                    onClick={() => toggleSpec(spec)}
                    className={`rounded-full px-3 py-1 text-sm transition-colors ${
                      selected
                        ? "bg-indigo-600 text-white"
                        : "border border-gray-300 text-gray-700 hover:border-indigo-400"
                    }`}
                  >
                    {spec}
                  </button>
                );
              })}
            </div>
          </div>

          <Button
            onClick={() => handleSearch(1)}
            className="w-full sm:w-auto bg-indigo-600 hover:bg-indigo-700"
            disabled={loading}
          >
            {loading ? (
              <Loader2 className="mr-2 h-4 w-4 animate-spin" />
            ) : (
              <Search className="mr-2 h-4 w-4" />
            )}
            Cerca
          </Button>
        </CardContent>
      </Card>

      {/* Results */}
      {error && (
        <Alert variant="destructive">
          <AlertDescription>{error}</AlertDescription>
        </Alert>
      )}

      {results && (
        <div className="space-y-4">
          <p className="text-sm text-gray-500">
            {results.total} professionisti trovati
            {results.total > 0 && ` — pagina ${results.page} di ${results.pages}`}
          </p>

          {results.items.length === 0 ? (
            <Card>
              <CardContent className="py-12 text-center text-gray-500">
                Nessun professionista trovato con i filtri selezionati.
              </CardContent>
            </Card>
          ) : (
            <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-3">
              {results.items.map((pro) => (
                <Link key={pro.user_id} href={`/profiles/${pro.user_id}`}>
                  <Card className="h-full hover:shadow-md transition-shadow cursor-pointer">
                    <CardContent className="p-4 space-y-3">
                      <div className="flex items-start justify-between">
                        <div>
                          <div className="flex items-center gap-1">
                            {pro.is_featured && (
                              <Star className="h-3.5 w-3.5 text-yellow-500 fill-yellow-500" />
                            )}
                            <p className="font-semibold text-gray-900">
                              {pro.first_name} {pro.last_name}
                            </p>
                          </div>
                          {pro.preferred_city && (
                            <p className="text-xs text-gray-500 flex items-center gap-1 mt-0.5">
                              <MapPin className="h-3 w-3" />
                              {pro.preferred_city}
                              {pro.preferred_province && `, ${pro.preferred_province}`}
                            </p>
                          )}
                        </div>
                        <span
                          className={`rounded-full px-2 py-0.5 text-xs font-medium ${
                            AVAILABILITY_COLORS[pro.availability_status]
                          }`}
                        >
                          {AVAILABILITY_LABELS[pro.availability_status]}
                        </span>
                      </div>

                      {pro.bio && (
                        <p className="text-sm text-gray-600 line-clamp-2">{pro.bio}</p>
                      )}

                      <div className="flex flex-wrap gap-1">
                        {pro.specializations.slice(0, 3).map((s) => (
                          <span
                            key={s}
                            className="rounded-full bg-indigo-50 px-2 py-0.5 text-xs text-indigo-700"
                          >
                            {s}
                          </span>
                        ))}
                        {pro.specializations.length > 3 && (
                          <span className="text-xs text-gray-400">
                            +{pro.specializations.length - 3}
                          </span>
                        )}
                      </div>

                      {pro.years_of_experience !== null && (
                        <p className="text-xs text-gray-500 flex items-center gap-1">
                          <Briefcase className="h-3 w-3" />
                          {pro.years_of_experience} anni di esperienza
                        </p>
                      )}
                    </CardContent>
                  </Card>
                </Link>
              ))}
            </div>
          )}

          {/* Pagination */}
          {results.pages > 1 && (
            <div className="flex items-center justify-center gap-2">
              <Button
                variant="outline"
                size="sm"
                disabled={page <= 1 || loading}
                onClick={() => handleSearch(page - 1)}
              >
                Precedente
              </Button>
              <span className="text-sm text-gray-600">
                {page} / {results.pages}
              </span>
              <Button
                variant="outline"
                size="sm"
                disabled={page >= results.pages || loading}
                onClick={() => handleSearch(page + 1)}
              >
                Successiva
              </Button>
            </div>
          )}
        </div>
      )}
    </div>
  );
}
