"use client";

import { useEffect, useState } from "react";
import { Loader2, ArrowLeft, CheckCircle2, AlertCircle } from "lucide-react";
import Link from "next/link";
import { Button } from "@/components/ui/button";
import { Alert, AlertDescription } from "@/components/ui/alert";
import { SalonProfileForm } from "@/components/profile/SalonProfileForm";
import { useAuth } from "@/hooks/useAuth";
import { apiGetPublicProfile } from "@/lib/api/profile";
import type { SalonProfile } from "@/types/profile";

export default function SalonSettingsPage() {
  const { user } = useAuth();
  const [profile, setProfile] = useState<SalonProfile | null>(null);
  const [loading, setLoading] = useState(true);
  const [fetchError, setFetchError] = useState<string | null>(null);

  useEffect(() => {
    if (!user?.id) return;

    apiGetPublicProfile(user.id)
      .then((data) => {
        // data.profile is SalonProfile if role = salon
        if ("business_name" in data.profile) {
          setProfile(data.profile as SalonProfile);
        }
      })
      .catch((err) => {
        setFetchError(err instanceof Error ? err.message : "Errore nel caricamento del profilo");
      })
      .finally(() => setLoading(false));
  }, [user?.id]);

  if (loading) {
    return (
      <div className="flex items-center justify-center py-20">
        <Loader2 className="h-8 w-8 animate-spin text-indigo-600" />
      </div>
    );
  }

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
          <h1 className="text-2xl font-bold text-gray-900">Impostazioni profilo</h1>
          <p className="text-sm text-gray-500">Aggiorna le informazioni del tuo salone</p>
        </div>
      </div>

      {profile?.is_profile_complete ? (
        <Alert className="border-green-200 bg-green-50 text-green-800">
          <CheckCircle2 className="h-4 w-4" />
          <AlertDescription>Il tuo profilo è completo! Sarà visibile ai professionisti in cerca di lavoro.</AlertDescription>
        </Alert>
      ) : (
        <Alert className="border-amber-200 bg-amber-50 text-amber-800">
          <AlertCircle className="h-4 w-4" />
          <AlertDescription>
            Completa il profilo aggiungendo almeno: nome salone, telefono, indirizzo e una descrizione.
          </AlertDescription>
        </Alert>
      )}

      {fetchError ? (
        <Alert variant="destructive">
          <AlertDescription>{fetchError}</AlertDescription>
        </Alert>
      ) : profile ? (
        <SalonProfileForm
          initialProfile={profile}
          onUpdate={(updated) => setProfile(updated)}
        />
      ) : null}
    </div>
  );
}
