"use client";

import { useState } from "react";
import { useForm } from "react-hook-form";
import { zodResolver } from "@hookform/resolvers/zod";
import { z } from "zod";
import Link from "next/link";
import { Loader2, Mail, CheckCircle2 } from "lucide-react";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Alert, AlertDescription } from "@/components/ui/alert";
import { apiRequestPasswordReset } from "@/lib/api/auth";

const schema = z.object({
  email: z.string().email("Inserisci un'email valida"),
});

type FormValues = z.infer<typeof schema>;

export function RequestResetForm() {
  const [sent, setSent] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const {
    register,
    handleSubmit,
    formState: { errors, isSubmitting },
  } = useForm<FormValues>({ resolver: zodResolver(schema) });

  const onSubmit = async (values: FormValues) => {
    setError(null);
    try {
      await apiRequestPasswordReset(values.email);
      setSent(true);
    } catch {
      setError("Errore nella richiesta. Riprova tra qualche minuto.");
    }
  };

  if (sent) {
    return (
      <div className="text-center py-4">
        <div className="mx-auto mb-4 flex h-16 w-16 items-center justify-center rounded-full bg-green-100">
          <CheckCircle2 className="h-8 w-8 text-green-600" />
        </div>
        <h3 className="text-lg font-semibold text-gray-900 mb-2">Email inviata!</h3>
        <p className="text-sm text-gray-500 mb-6">
          Se l&apos;email è registrata, riceverai le istruzioni per reimpostare la password.
          Controlla anche la cartella spam.
        </p>
        <Link href="/login">
          <Button variant="outline" className="w-full">
            Torna al login
          </Button>
        </Link>
      </div>
    );
  }

  return (
    <form onSubmit={handleSubmit(onSubmit)} className="space-y-4">
      {error && (
        <Alert variant="destructive">
          <AlertDescription>{error}</AlertDescription>
        </Alert>
      )}

      <div className="space-y-1">
        <Label htmlFor="email">Email</Label>
        <div className="relative">
          <Mail className="absolute left-3 top-1/2 -translate-y-1/2 h-4 w-4 text-gray-400" />
          <Input
            id="email"
            type="email"
            placeholder="tua@email.com"
            className="pl-10"
            {...register("email")}
          />
        </div>
        {errors.email && (
          <p className="text-xs text-red-500">{errors.email.message}</p>
        )}
      </div>

      <Button type="submit" className="w-full" disabled={isSubmitting}>
        {isSubmitting ? (
          <>
            <Loader2 className="mr-2 h-4 w-4 animate-spin" />
            Invio in corso…
          </>
        ) : (
          "Invia link di reset"
        )}
      </Button>

      <p className="text-center text-sm text-gray-500">
        Ricordi la password?{" "}
        <Link href="/login" className="text-indigo-600 hover:underline font-medium">
          Accedi
        </Link>
      </p>
    </form>
  );
}
