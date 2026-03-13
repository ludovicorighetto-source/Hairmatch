"use client";

import { useState } from "react";
import { useForm, Controller } from "react-hook-form";
import { zodResolver } from "@hookform/resolvers/zod";
import { z } from "zod";
import { Loader2, Save, CheckCircle2 } from "lucide-react";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Alert, AlertDescription } from "@/components/ui/alert";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { apiUpdateProfessionalProfile } from "@/lib/api/profile";
import type { ProfessionalProfile } from "@/types/profile";
import { SPECIALIZATIONS, ITALIAN_PROVINCES } from "@/types/auth";

const CONTRACT_TYPES = [
  { value: "full_time", label: "Dipendente full-time" },
  { value: "part_time", label: "Dipendente part-time" },
  { value: "freelance", label: "Freelance / P.IVA" },
  { value: "apprenticeship", label: "Apprendistato" },
];

const AVAILABILITY_OPTIONS = [
  { value: "available", label: "Disponibile subito" },
  { value: "partially_available", label: "Parzialmente disponibile" },
  { value: "not_available", label: "Non disponibile" },
  { value: "on_leave", label: "In pausa" },
];

const schema = z.object({
  first_name: z.string().min(1, "Campo obbligatorio").max(100),
  last_name: z.string().min(1, "Campo obbligatorio").max(100),
  phone: z.string().min(6, "Numero non valido").max(30),
  bio: z.string().max(2000).optional().or(z.literal("")),
  specializations: z.array(z.string()).min(1, "Seleziona almeno una specializzazione"),
  years_of_experience: z.coerce.number().min(0).max(80).optional(),
  preferred_city: z.string().max(100).optional().or(z.literal("")),
  preferred_province: z.string().max(5).optional().or(z.literal("")),
  max_travel_km: z.coerce.number().min(0).max(1000).optional(),
  is_available_remotely: z.boolean().optional(),
  preferred_contract_types: z.array(z.string()).optional(),
  availability_status: z.enum([
    "available",
    "partially_available",
    "not_available",
    "on_leave",
  ]),
});

type FormValues = z.infer<typeof schema>;

interface Props {
  initialProfile: ProfessionalProfile;
  onUpdate?: (profile: ProfessionalProfile) => void;
}

export function ProfessionalProfileForm({ initialProfile, onUpdate }: Props) {
  const [success, setSuccess] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const {
    register,
    handleSubmit,
    control,
    watch,
    formState: { errors, isSubmitting, isDirty },
  } = useForm<FormValues>({
    resolver: zodResolver(schema),
    defaultValues: {
      first_name: initialProfile.first_name,
      last_name: initialProfile.last_name,
      phone: initialProfile.phone,
      bio: initialProfile.bio ?? "",
      specializations: initialProfile.specializations,
      years_of_experience: initialProfile.years_of_experience ?? undefined,
      preferred_city: initialProfile.preferred_city ?? "",
      preferred_province: initialProfile.preferred_province ?? "",
      max_travel_km: initialProfile.max_travel_km,
      is_available_remotely: initialProfile.is_available_remotely,
      preferred_contract_types: initialProfile.preferred_contract_types,
      availability_status: initialProfile.availability_status,
    },
  });

  const selectedSpecializations = watch("specializations") ?? [];
  const selectedContracts = watch("preferred_contract_types") ?? [];

  const onSubmit = async (values: FormValues) => {
    setError(null);
    setSuccess(false);

    try {
      const updated = await apiUpdateProfessionalProfile({
        first_name: values.first_name,
        last_name: values.last_name,
        phone: values.phone,
        bio: values.bio || undefined,
        specializations: values.specializations,
        years_of_experience: values.years_of_experience,
        preferred_city: values.preferred_city || undefined,
        preferred_province: values.preferred_province || undefined,
        max_travel_km: values.max_travel_km,
        is_available_remotely: values.is_available_remotely,
        preferred_contract_types: values.preferred_contract_types,
        availability_status: values.availability_status,
      });
      setSuccess(true);
      onUpdate?.(updated);
      setTimeout(() => setSuccess(false), 3000);
    } catch (err) {
      setError(err instanceof Error ? err.message : "Errore nel salvataggio");
    }
  };

  return (
    <form onSubmit={handleSubmit(onSubmit)} className="space-y-6">
      {error && (
        <Alert variant="destructive">
          <AlertDescription>{error}</AlertDescription>
        </Alert>
      )}
      {success && (
        <Alert className="border-green-200 bg-green-50 text-green-800">
          <CheckCircle2 className="h-4 w-4" />
          <AlertDescription>Profilo aggiornato con successo!</AlertDescription>
        </Alert>
      )}

      {/* Personal info */}
      <Card>
        <CardHeader>
          <CardTitle className="text-base">Informazioni personali</CardTitle>
        </CardHeader>
        <CardContent className="grid gap-4 sm:grid-cols-2">
          <div className="space-y-1">
            <Label htmlFor="first_name">Nome *</Label>
            <Input id="first_name" {...register("first_name")} />
            {errors.first_name && (
              <p className="text-xs text-red-500">{errors.first_name.message}</p>
            )}
          </div>

          <div className="space-y-1">
            <Label htmlFor="last_name">Cognome *</Label>
            <Input id="last_name" {...register("last_name")} />
            {errors.last_name && (
              <p className="text-xs text-red-500">{errors.last_name.message}</p>
            )}
          </div>

          <div className="space-y-1">
            <Label htmlFor="phone">Telefono *</Label>
            <Input id="phone" type="tel" {...register("phone")} />
            {errors.phone && (
              <p className="text-xs text-red-500">{errors.phone.message}</p>
            )}
          </div>

          <div className="space-y-1">
            <Label htmlFor="years_of_experience">Anni di esperienza</Label>
            <Input id="years_of_experience" type="number" min={0} max={80} {...register("years_of_experience")} />
          </div>

          <div className="space-y-1 sm:col-span-2">
            <Label htmlFor="bio">Bio / Presentazione</Label>
            <textarea
              id="bio"
              rows={4}
              className="w-full rounded-md border border-input bg-transparent px-3 py-2 text-sm shadow-sm placeholder:text-muted-foreground focus:outline-none focus:ring-1 focus:ring-ring"
              placeholder="Racconta di te, della tua formazione e delle tue passioni..."
              {...register("bio")}
            />
          </div>
        </CardContent>
      </Card>

      {/* Specializations */}
      <Card>
        <CardHeader>
          <CardTitle className="text-base">Specializzazioni *</CardTitle>
        </CardHeader>
        <CardContent>
          <Controller
            name="specializations"
            control={control}
            render={({ field }) => (
              <div className="flex flex-wrap gap-2">
                {SPECIALIZATIONS.map((spec) => {
                  const selected = field.value.includes(spec);
                  return (
                    <button
                      key={spec}
                      type="button"
                      onClick={() => {
                        const next = selected
                          ? field.value.filter((s) => s !== spec)
                          : [...field.value, spec];
                        field.onChange(next);
                      }}
                      className={`rounded-full px-4 py-1.5 text-sm font-medium transition-colors ${
                        selected
                          ? "bg-violet-600 text-white"
                          : "border border-gray-300 text-gray-700 hover:border-violet-400 hover:text-violet-600"
                      }`}
                    >
                      {spec}
                    </button>
                  );
                })}
              </div>
            )}
          />
          {errors.specializations && (
            <p className="mt-2 text-xs text-red-500">{errors.specializations.message}</p>
          )}
        </CardContent>
      </Card>

      {/* Availability & preferences */}
      <Card>
        <CardHeader>
          <CardTitle className="text-base">Disponibilità e preferenze</CardTitle>
        </CardHeader>
        <CardContent className="grid gap-4 sm:grid-cols-2">
          <div className="space-y-1">
            <Label htmlFor="availability_status">Stato disponibilità *</Label>
            <select
              id="availability_status"
              className="w-full rounded-md border border-input bg-transparent px-3 py-2 text-sm shadow-sm focus:outline-none focus:ring-1 focus:ring-ring"
              {...register("availability_status")}
            >
              {AVAILABILITY_OPTIONS.map((o) => (
                <option key={o.value} value={o.value}>{o.label}</option>
              ))}
            </select>
          </div>

          <div className="space-y-1">
            <Label htmlFor="max_travel_km">Raggio disponibilità (km)</Label>
            <Input id="max_travel_km" type="number" min={0} max={1000} {...register("max_travel_km")} />
          </div>

          <div className="space-y-1">
            <Label htmlFor="preferred_city">Città preferita</Label>
            <Input id="preferred_city" {...register("preferred_city")} />
          </div>

          <div className="space-y-1">
            <Label htmlFor="preferred_province">Provincia preferita</Label>
            <select
              id="preferred_province"
              className="w-full rounded-md border border-input bg-transparent px-3 py-2 text-sm shadow-sm focus:outline-none focus:ring-1 focus:ring-ring"
              {...register("preferred_province")}
            >
              <option value="">Qualsiasi</option>
              {ITALIAN_PROVINCES.map((p) => (
                <option key={p} value={p}>{p}</option>
              ))}
            </select>
          </div>

          <div className="sm:col-span-2 flex items-center gap-2">
            <input
              id="is_available_remotely"
              type="checkbox"
              className="h-4 w-4 rounded border-gray-300 text-violet-600 focus:ring-violet-500"
              {...register("is_available_remotely")}
            />
            <Label htmlFor="is_available_remotely">Disponibile per lavoro da remoto</Label>
          </div>

          <div className="sm:col-span-2 space-y-2">
            <Label>Tipologie contrattuali preferite</Label>
            <Controller
              name="preferred_contract_types"
              control={control}
              render={({ field }) => (
                <div className="flex flex-wrap gap-2">
                  {CONTRACT_TYPES.map((ct) => {
                    const selected = (field.value ?? []).includes(ct.value);
                    return (
                      <button
                        key={ct.value}
                        type="button"
                        onClick={() => {
                          const current = field.value ?? [];
                          const next = selected
                            ? current.filter((v) => v !== ct.value)
                            : [...current, ct.value];
                          field.onChange(next);
                        }}
                        className={`rounded-full px-3 py-1 text-sm transition-colors ${
                          selected
                            ? "bg-violet-600 text-white"
                            : "border border-gray-300 text-gray-700 hover:border-violet-400"
                        }`}
                      >
                        {ct.label}
                      </button>
                    );
                  })}
                </div>
              )}
            />
          </div>
        </CardContent>
      </Card>

      <Button
        type="submit"
        className="w-full bg-violet-600 hover:bg-violet-700"
        disabled={isSubmitting || !isDirty}
      >
        {isSubmitting ? (
          <>
            <Loader2 className="mr-2 h-4 w-4 animate-spin" />
            Salvataggio…
          </>
        ) : (
          <>
            <Save className="mr-2 h-4 w-4" />
            Salva modifiche
          </>
        )}
      </Button>
    </form>
  );
}
