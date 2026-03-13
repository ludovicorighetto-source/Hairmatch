"use client";

import { useState, useCallback } from "react";
import Link from "next/link";
import { ArrowLeft, Search, Star, MapPin, Scissors, Loader2 } from "lucide-react";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Card, CardContent } from "@/components/ui/card";
import { Alert, AlertDescription } from "@/components/ui/alert";
import { apiSearchSalons } from "@/lib/api/search";
import type { SalonCard, PaginatedResult } from "@/types/search";
import { ITALIAN_PROVINCES } from "@/types/auth";

export default function ProfessionalSearchPage() {
  const [city, setCity] = useState("");
  const [province, setProvince] = useState("");
  const [results, setResults] = useState<PaginatedResult<SalonCard> | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [page, setPage] = useState(1);

  const handleSearch = useCallback(
    async (searchPage = 1) => {
      setLoading(true);
      setError(null);
      setPage(searchPage);
      try {
        const data = await apiSearchSalons({
          city: city || undefined,
          province: province || undefined,
          page: searchPage,
          limit: 12,
        });
        setResults(data);
      } catch {
        setError("Errore nella ricerca. Riprova.");
      } finally {
        setLoading(false);
      }
    },
    [city, province]
  );

  return (
    <div className="space-y-6">
      <div className="flex items-center gap-4">
        <Link href="/dashboard/professional">
          <Button variant="ghost" size="sm" className="flex items-center gap-2">
            <ArrowLeft className="h-4 w-4" />
            Dashboard
          </Button>
        </Link>
        <div>
          <h1 className="text-2xl font-bold text-gray-900">Cerca Saloni</h1>
          <p className="text-sm text-gray-500">Esplora i saloni che cercano professionisti come te</p>
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
                placeholder="es. Roma"
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

          <Button
            onClick={() => handleSearch(1)}
            className="w-full sm:w-auto bg-violet-600 hover:bg-violet-700"
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
            {results.total} saloni trovati
            {results.total > 0 && ` — pagina ${results.page} di ${results.pages}`}
          </p>

          {results.items.length === 0 ? (
            <Card>
              <CardContent className="py-12 text-center text-gray-500">
                Nessun salone trovato con i filtri selezionati.
              </CardContent>
            </Card>
          ) : (
            <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-3">
              {results.items.map((salon) => (
                <Link key={salon.user_id} href={`/profiles/${salon.user_id}`}>
                  <Card className="h-full hover:shadow-md transition-shadow cursor-pointer">
                    <CardContent className="p-4 space-y-3">
                      <div className="flex items-start justify-between">
                        <div>
                          <div className="flex items-center gap-1">
                            {salon.is_featured && (
                              <Star className="h-3.5 w-3.5 text-yellow-500 fill-yellow-500" />
                            )}
                            <p className="font-semibold text-gray-900">{salon.business_name}</p>
                          </div>
                          <p className="text-xs text-gray-500 flex items-center gap-1 mt-0.5">
                            <MapPin className="h-3 w-3" />
                            {salon.address_city}, {salon.address_province}
                          </p>
                        </div>
                        {salon.distance_km !== null && (
                          <span className="text-xs text-gray-500">{salon.distance_km} km</span>
                        )}
                      </div>

                      {salon.description && (
                        <p className="text-sm text-gray-600 line-clamp-2">{salon.description}</p>
                      )}

                      {salon.seats_count && (
                        <p className="text-xs text-gray-500 flex items-center gap-1">
                          <Scissors className="h-3 w-3" />
                          {salon.seats_count} postazioni
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
