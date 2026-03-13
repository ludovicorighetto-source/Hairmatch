"use client";

import { useState } from "react";
import { useForm } from "react-hook-form";
import { zodResolver } from "@hookform/resolvers/zod";
import { z } from "zod";
import { Loader2, Save, CheckCircle2 } from "lucide-react";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Alert, AlertDescription } from "@/components/ui/alert";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { apiUpdateSalonProfile } from "@/lib/api/profile";
import type { SalonProfile } from "@/types/profile";
import { ITALIAN_PROVINCES } from "@/types/auth";

const schema = z.object({
  business_name: z.string().min(1, "Campo obbligatorio").max(255),
  phone: z.string().min(6, "Numero non valido").max(30),
  description: z.string().max(2000).optional().or(z.literal("")),
  website_url: z.string().url("URL non valido").optional().or(z.literal("")),
  vat_number: z.string().max(20).optional().or(z.literal("")),
  address_street: z.string().min(1, "Campo obbligatorio").max(255),
  address_city: z.string().min(1, "Campo obbligatorio").max(100),
  address_province: z.string().min(2).max(5),
  address_postal_code: z.string().min(4).max(10),
  seats_count: z.coerce.number().min(1).max(500).optional(),
});

type FormValues = z.infer<typeof schema>;

interface Props {
  initialProfile: SalonProfile;
  onUpdate?: (profile: SalonProfile) => void;
}

export function SalonProfileForm({ initialProfile, onUpdate }: Props) {
  const [success, setSuccess] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const {
    register,
    handleSubmit,
    formState: { errors, isSubmitting, isDirty },
  } = useForm<FormValues>({
    resolver: zodResolver(schema),
    defaultValues: {
      business_name: initialProfile.business_name,
      phone: initialProfile.phone,
      description: initialProfile.description ?? "",
      website_url: initialProfile.website_url ?? "",
      vat_number: initialProfile.vat_number ?? "",
      address_street: initialProfile.address_street,
      address_city: initialProfile.address_city,
      address_province: initialProfile.address_province,
      address_postal_code: initialProfile.address_postal_code,
      seats_count: initialProfile.seats_count ?? undefined,
    },
  });

  const onSubmit = async (values: FormValues) => {
    setError(null);
    setSuccess(false);

    try {
      const updated = await apiUpdateSalonProfile({
        business_name: values.business_name,
        phone: values.phone,
        description: values.description || undefined,
        website_url: values.website_url || undefined,
        vat_number: values.vat_number || undefined,
        address_street: values.address_street,
        address_city: values.address_city,
        address_province: values.address_province,
        address_postal_code: values.address_postal_code,
        seats_count: values.seats_count,
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

      {/* Basic info */}
      <Card>
        <CardHeader>
          <CardTitle className="text-base">Informazioni principali</CardTitle>
        </CardHeader>
        <CardContent className="grid gap-4 sm:grid-cols-2">
          <div className="space-y-1 sm:col-span-2">
            <Label htmlFor="business_name">Nome salone *</Label>
            <Input id="business_name" {...register("business_name")} />
            {errors.business_name && (
              <p className="text-xs text-red-500">{errors.business_name.message}</p>
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
            <Label htmlFor="seats_count">Numero postazioni</Label>
            <Input id="seats_count" type="number" min={1} max={500} {...register("seats_count")} />
            {errors.seats_count && (
              <p className="text-xs text-red-500">{errors.seats_count.message}</p>
            )}
          </div>

          <div className="space-y-1 sm:col-span-2">
            <Label htmlFor="description">Descrizione</Label>
            <textarea
              id="description"
              rows={4}
              className="w-full rounded-md border border-input bg-transparent px-3 py-2 text-sm shadow-sm placeholder:text-muted-foreground focus:outline-none focus:ring-1 focus:ring-ring"
              placeholder="Descrivi il tuo salone, i servizi offerti, l'atmosfera..."
              {...register("description")}
            />
            {errors.description && (
              <p className="text-xs text-red-500">{errors.description.message}</p>
            )}
          </div>

          <div className="space-y-1">
            <Label htmlFor="website_url">Sito web</Label>
            <Input id="website_url" type="url" placeholder="https://..." {...register("website_url")} />
            {errors.website_url && (
              <p className="text-xs text-red-500">{errors.website_url.message}</p>
            )}
          </div>

          <div className="space-y-1">
            <Label htmlFor="vat_number">Partita IVA</Label>
            <Input id="vat_number" {...register("vat_number")} />
          </div>
        </CardContent>
      </Card>

      {/* Address */}
      <Card>
        <CardHeader>
          <CardTitle className="text-base">Indirizzo</CardTitle>
        </CardHeader>
        <CardContent className="grid gap-4 sm:grid-cols-2">
          <div className="space-y-1 sm:col-span-2">
            <Label htmlFor="address_street">Via / Piazza *</Label>
            <Input id="address_street" {...register("address_street")} />
            {errors.address_street && (
              <p className="text-xs text-red-500">{errors.address_street.message}</p>
            )}
          </div>

          <div className="space-y-1">
            <Label htmlFor="address_city">Città *</Label>
            <Input id="address_city" {...register("address_city")} />
            {errors.address_city && (
              <p className="text-xs text-red-500">{errors.address_city.message}</p>
            )}
          </div>

          <div className="space-y-1">
            <Label htmlFor="address_province">Provincia *</Label>
            <select
              id="address_province"
              className="w-full rounded-md border border-input bg-transparent px-3 py-2 text-sm shadow-sm focus:outline-none focus:ring-1 focus:ring-ring"
              {...register("address_province")}
            >
              <option value="">Seleziona</option>
              {ITALIAN_PROVINCES.map((p) => (
                <option key={p} value={p}>{p}</option>
              ))}
            </select>
            {errors.address_province && (
              <p className="text-xs text-red-500">{errors.address_province.message}</p>
            )}
          </div>

          <div className="space-y-1">
            <Label htmlFor="address_postal_code">CAP *</Label>
            <Input id="address_postal_code" maxLength={5} {...register("address_postal_code")} />
            {errors.address_postal_code && (
              <p className="text-xs text-red-500">{errors.address_postal_code.message}</p>
            )}
          </div>
        </CardContent>
      </Card>

      <Button
        type="submit"
        className="w-full bg-indigo-600 hover:bg-indigo-700"
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
