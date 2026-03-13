"use client";

import { useRouter } from "next/navigation";
import Link from "next/link";
import {
  Briefcase,
  Users,
  LogOut,
  Loader2,
  Building2,
  TrendingUp,
  Settings,
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

export default function SalonDashboardPage() {
  const { user, logout, isLoading } = useAuth();
  const router = useRouter();

  const handleLogout = async () => {
    await logout();
    router.push("/login");
  };

  if (!user) {
    return (
      <div className="flex items-center justify-center py-20">
        <Loader2 className="h-8 w-8 animate-spin text-indigo-600" />
      </div>
    );
  }

  return (
    <div className="space-y-8">
      {/* Welcome header */}
      <div className="flex flex-col gap-4 sm:flex-row sm:items-start sm:justify-between">
        <div>
          <div className="flex items-center gap-2 text-sm text-gray-500">
            <Building2 className="h-4 w-4" />
            <span>Dashboard Salone</span>
          </div>
          <h1 className="mt-1 text-2xl font-bold text-gray-900 sm:text-3xl">
            Benvenuto, {user.business_name || user.email}!
          </h1>
          <p className="mt-1 text-gray-600">
            Gestisci il tuo salone e trova i migliori professionisti.
          </p>
        </div>
        <div className="flex items-center gap-2 self-start">
          <Link href="/dashboard/salon/settings">
            <Button variant="outline" size="sm" className="flex items-center gap-2">
              <Settings className="h-4 w-4" />
              Impostazioni
            </Button>
          </Link>
          <Button
          variant="outline"
          onClick={handleLogout}
          disabled={isLoading}
          className="flex items-center gap-2"
        >
          {isLoading ? (
            <Loader2 className="h-4 w-4 animate-spin" />
          ) : (
            <LogOut className="h-4 w-4" />
          )}
          Esci
        </Button>
        </div>
      </div>

      {/* Stats overview */}
      <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-4">
        <Card>
          <CardHeader className="pb-2">
            <CardDescription>Annunci attivi</CardDescription>
            <CardTitle className="text-3xl">0</CardTitle>
          </CardHeader>
          <CardContent>
            <p className="text-xs text-muted-foreground">
              Nessun annuncio pubblicato
            </p>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="pb-2">
            <CardDescription>Candidature ricevute</CardDescription>
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
            <CardDescription>Professionisti salvati</CardDescription>
            <CardTitle className="text-3xl">0</CardTitle>
          </CardHeader>
          <CardContent>
            <p className="text-xs text-muted-foreground">
              Nessun profilo salvato
            </p>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="pb-2">
            <CardDescription>Visualizzazioni profilo</CardDescription>
            <CardTitle className="text-3xl">0</CardTitle>
          </CardHeader>
          <CardContent>
            <p className="text-xs text-muted-foreground">
              Inizia pubblicando un annuncio
            </p>
          </CardContent>
        </Card>
      </div>

      {/* Action cards */}
      <div className="grid gap-6 sm:grid-cols-2">
        <Card className="border-dashed">
          <CardContent className="flex flex-col items-center justify-center p-8 text-center">
            <div className="mb-4 flex h-14 w-14 items-center justify-center rounded-full bg-indigo-100">
              <Briefcase className="h-7 w-7 text-indigo-600" />
            </div>
            <h3 className="mb-2 font-semibold text-gray-900">
              Pubblica un annuncio
            </h3>
            <p className="mb-4 text-sm text-gray-500">
              Descrivi la posizione che cerchi e inizia a ricevere candidature
              dai professionisti qualificati nella tua zona.
            </p>
            <Link href="/dashboard/salon/jobs">
              <Button className="bg-indigo-600 hover:bg-indigo-700">
                Gestisci annunci
              </Button>
            </Link>
          </CardContent>
        </Card>

        <Card className="border-dashed">
          <CardContent className="flex flex-col items-center justify-center p-8 text-center">
            <div className="mb-4 flex h-14 w-14 items-center justify-center rounded-full bg-violet-100">
              <Users className="h-7 w-7 text-violet-600" />
            </div>
            <h3 className="mb-2 font-semibold text-gray-900">
              Sfoglia i professionisti
            </h3>
            <p className="mb-4 text-sm text-gray-500">
              Esplora i profili dei professionisti disponibili nella tua zona
              e contattali direttamente.
            </p>
            <Link href="/dashboard/salon/search">
              <Button
                variant="outline"
                className="border-violet-500 text-violet-700 hover:bg-violet-50"
              >
                Cerca professionisti
              </Button>
            </Link>
          </CardContent>
        </Card>
      </div>

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
              <dt className="text-xs font-medium text-gray-500">Email</dt>
              <dd className="text-sm text-gray-900">{user.email}</dd>
            </div>
            <div>
              <dt className="text-xs font-medium text-gray-500">Ruolo</dt>
              <dd className="inline-flex items-center rounded-full bg-indigo-100 px-2 py-0.5 text-xs font-medium text-indigo-700">
                Salone
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
