"use client";

import { useRouter } from "next/navigation";
import Link from "next/link";
import {
  Briefcase,
  Building2,
  LogOut,
  Loader2,
  UserCircle,
  TrendingUp,
  ToggleLeft,
  ToggleRight,
  Settings,
} from "lucide-react";
import { useState } from "react";
import { useAuth } from "@/hooks/useAuth";
import { Button } from "@/components/ui/button";
import {
  Card,
  CardContent,
  CardHeader,
  CardTitle,
  CardDescription,
} from "@/components/ui/card";
import { cn } from "@/lib/utils";
import { RecommendedJobsPanel } from "@/components/matching/RecommendedJobsPanel";

export default function ProfessionalDashboardPage() {
  const { user, accessToken, logout, isLoading } = useAuth();
  const router = useRouter();
  const [isAvailable, setIsAvailable] = useState(true);

  const handleLogout = async () => {
    await logout();
    router.push("/login");
  };

  if (!user) {
    return (
      <div className="flex items-center justify-center py-20">
        <Loader2 className="h-8 w-8 animate-spin text-violet-600" />
      </div>
    );
  }

  const displayName = user.first_name
    ? `${user.first_name}${user.last_name ? ` ${user.last_name}` : ""}`
    : user.email;

  return (
    <div className="space-y-8">
      {/* Welcome header */}
      <div className="flex flex-col gap-4 sm:flex-row sm:items-start sm:justify-between">
        <div>
          <div className="flex items-center gap-2 text-sm text-gray-500">
            <UserCircle className="h-4 w-4" />
            <span>Dashboard Professionista</span>
          </div>
          <h1 className="mt-1 text-2xl font-bold text-gray-900 sm:text-3xl">
            Benvenuto, {user.first_name || user.email}!
          </h1>
          <p className="mt-1 text-gray-600">
            Gestisci il tuo profilo e trova le migliori opportunità.
          </p>
        </div>
        <Button
          variant="outline"
          onClick={handleLogout}
          disabled={isLoading}
          className="flex items-center gap-2 self-start"
        >
          {isLoading ? (
            <Loader2 className="h-4 w-4 animate-spin" />
          ) : (
            <LogOut className="h-4 w-4" />
          )}
          Esci
        </Button>
      </div>

      {/* Availability toggle */}
      <Card
        className={cn(
          "border-2 transition-colors",
          isAvailable ? "border-green-200 bg-green-50" : "border-gray-200"
        )}
      >
        <CardContent className="flex items-center justify-between p-4">
          <div>
            <p className="font-medium text-gray-900">Stato disponibilità</p>
            <p className="text-sm text-gray-600">
              {isAvailable
                ? "Sei visibile ai saloni che cercano professionisti"
                : "Il tuo profilo non è visibile ai saloni"}
            </p>
          </div>
          <button
            type="button"
            onClick={() => setIsAvailable((v) => !v)}
            className={cn(
              "flex items-center gap-2 rounded-full px-4 py-2 text-sm font-medium transition-colors",
              isAvailable
                ? "bg-green-600 text-white hover:bg-green-700"
                : "bg-gray-200 text-gray-700 hover:bg-gray-300"
            )}
            aria-pressed={isAvailable}
            aria-label="Cambia stato disponibilità"
          >
            {isAvailable ? (
              <>
                <ToggleRight className="h-5 w-5" />
                Disponibile
              </>
            ) : (
              <>
                <ToggleLeft className="h-5 w-5" />
                Non disponibile
              </>
            )}
          </button>
        </CardContent>
      </Card>

      {/* Stats overview */}
      <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-4">
        <Card>
          <CardHeader className="pb-2">
            <CardDescription>Candidature inviate</CardDescription>
            <CardTitle className="text-3xl">0</CardTitle>
          </CardHeader>
          <CardContent>
            <p className="text-xs text-muted-foreground">
              Nessuna candidatura ancora
            </p>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="pb-2">
            <CardDescription>Offerte disponibili</CardDescription>
            <CardTitle className="text-3xl">0</CardTitle>
          </CardHeader>
          <CardContent>
            <p className="text-xs text-muted-foreground">
              Nella tua zona
            </p>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="pb-2">
            <CardDescription>Saloni che ti hanno visto</CardDescription>
            <CardTitle className="text-3xl">0</CardTitle>
          </CardHeader>
          <CardContent>
            <p className="text-xs text-muted-foreground">
              Completa il profilo per più visibilità
            </p>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="pb-2">
            <CardDescription>Risposte ricevute</CardDescription>
            <CardTitle className="text-3xl">0</CardTitle>
          </CardHeader>
          <CardContent>
            <p className="text-xs text-muted-foreground">
              Dai saloni a cui ti sei candidato
            </p>
          </CardContent>
        </Card>
      </div>

      {/* Action cards */}
      <div className="grid gap-6 sm:grid-cols-2">
        <Card className="border-dashed">
          <CardContent className="flex flex-col items-center justify-center p-8 text-center">
            <div className="mb-4 flex h-14 w-14 items-center justify-center rounded-full bg-violet-100">
              <Briefcase className="h-7 w-7 text-violet-600" />
            </div>
            <h3 className="mb-2 font-semibold text-gray-900">
              Sfoglia le offerte
            </h3>
            <p className="mb-4 text-sm text-gray-500">
              Esplora le posizioni aperte nei saloni della tua zona e candidati
              con un click.
            </p>
            <Link href="/dashboard/professional/jobs">
              <Button className="bg-violet-600 hover:bg-violet-700">
                Cerca offerte
              </Button>
            </Link>
          </CardContent>
        </Card>

        <Card className="border-dashed">
          <CardContent className="flex flex-col items-center justify-center p-8 text-center">
            <div className="mb-4 flex h-14 w-14 items-center justify-center rounded-full bg-indigo-100">
              <Building2 className="h-7 w-7 text-indigo-600" />
            </div>
            <h3 className="mb-2 font-semibold text-gray-900">
              Esplora i saloni
            </h3>
            <p className="mb-4 text-sm text-gray-500">
              Scopri i saloni nelle vicinanze e invia una candidatura spontanea
              per farti notare.
            </p>
            <Link href="/dashboard/professional/settings">
              <Button
                variant="outline"
                className="border-indigo-500 text-indigo-700 hover:bg-indigo-50"
              >
                Impostazioni profilo
              </Button>
            </Link>
          </CardContent>
        </Card>
      </div>

      {/* Recommended jobs */}
      {accessToken && <RecommendedJobsPanel token={accessToken} />}

      {/* Account info */}
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center gap-2 text-base">
            <TrendingUp className="h-4 w-4" />
            Informazioni account
          </CardTitle>
        </CardHeader>
        <CardContent>
          <dl className="grid grid-cols-1 gap-3 sm:grid-cols-2">
            <div>
              <dt className="text-xs font-medium text-gray-500">Nome</dt>
              <dd className="text-sm text-gray-900">{displayName}</dd>
            </div>
            <div>
              <dt className="text-xs font-medium text-gray-500">Email</dt>
              <dd className="text-sm text-gray-900">{user.email}</dd>
            </div>
            <div>
              <dt className="text-xs font-medium text-gray-500">Ruolo</dt>
              <dd className="inline-flex items-center rounded-full bg-violet-100 px-2 py-0.5 text-xs font-medium text-violet-700">
                Professionista
              </dd>
            </div>
            <div>
              <dt className="text-xs font-medium text-gray-500">
                Email verificata
              </dt>
              <dd className="text-sm text-gray-900">
                {user.is_verified ? (
                  <span className="text-green-600">Verificata</span>
                ) : (
                  <span className="text-amber-600">In attesa di verifica</span>
                )}
              </dd>
            </div>
            <div>
              <dt className="text-xs font-medium text-gray-500">
                Stato account
              </dt>
              <dd className="text-sm text-gray-900">
                {user.is_active ? (
                  <span className="text-green-600">Attivo</span>
                ) : (
                  <span className="text-red-600">Disabilitato</span>
                )}
              </dd>
            </div>
          </dl>
        </CardContent>
      </Card>
    </div>
  );
}
