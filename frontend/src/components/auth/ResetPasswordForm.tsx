"use client";

import { useState } from "react";
import { useForm } from "react-hook-form";
import { zodResolver } from "@hookform/resolvers/zod";
import { z } from "zod";
import { useRouter } from "next/navigation";
import Link from "next/link";
import { Loader2, Eye, EyeOff, CheckCircle2 } from "lucide-react";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Alert, AlertDescription } from "@/components/ui/alert";
import { apiResetPassword } from "@/lib/api/auth";

const PASSWORD_REQUIREMENTS = [
  { label: "Almeno 8 caratteri", test: (p: string) => p.length >= 8 },
  { label: "Una lettera maiuscola", test: (p: string) => /[A-Z]/.test(p) },
  { label: "Un numero", test: (p: string) => /\d/.test(p) },
  { label: "Un carattere speciale", test: (p: string) => /[!@#$%^&*(),.?":{}|<>]/.test(p) },
];

const schema = z
  .object({
    new_password: z
      .string()
      .min(8, "La password deve avere almeno 8 caratteri")
      .regex(/[A-Z]/, "Deve contenere almeno una lettera maiuscola")
      .regex(/\d/, "Deve contenere almeno un numero")
      .regex(/[!@#$%^&*(),.?":{}|<>]/, "Deve contenere almeno un carattere speciale"),
    confirm_password: z.string(),
  })
  .refine((d) => d.new_password === d.confirm_password, {
    message: "Le password non corrispondono",
    path: ["confirm_password"],
  });

type FormValues = z.infer<typeof schema>;

interface Props {
  accessToken: string;
}

export function ResetPasswordForm({ accessToken }: Props) {
  const router = useRouter();
  const [showPassword, setShowPassword] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [success, setSuccess] = useState(false);

  const {
    register,
    handleSubmit,
    watch,
    formState: { errors, isSubmitting },
  } = useForm<FormValues>({ resolver: zodResolver(schema) });

  const password = watch("new_password", "");

  const onSubmit = async (values: FormValues) => {
    setError(null);

    if (!accessToken) {
      setError("Link non valido o scaduto. Richiedi un nuovo link di reset.");
      return;
    }

    try {
      await apiResetPassword(accessToken, values.new_password);
      setSuccess(true);
      setTimeout(() => router.push("/login"), 3000);
    } catch {
      setError("Link non valido o scaduto. Richiedi un nuovo link di reset.");
    }
  };

  if (success) {
    return (
      <div className="text-center py-4">
        <div className="mx-auto mb-4 flex h-16 w-16 items-center justify-center rounded-full bg-green-100">
          <CheckCircle2 className="h-8 w-8 text-green-600" />
        </div>
        <h3 className="text-lg font-semibold text-gray-900 mb-2">Password reimpostata!</h3>
        <p className="text-sm text-gray-500">
          Stai per essere reindirizzato al login…
        </p>
      </div>
    );
  }

  if (!accessToken) {
    return (
      <div className="text-center py-4">
        <Alert variant="destructive" className="mb-4">
          <AlertDescription>
            Link non valido o scaduto. Richiedi un nuovo link di reset.
          </AlertDescription>
        </Alert>
        <Link href="/request-reset">
          <Button variant="outline" className="w-full">
            Richiedi nuovo link
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
        <Label htmlFor="new_password">Nuova password</Label>
        <div className="relative">
          <Input
            id="new_password"
            type={showPassword ? "text" : "password"}
            placeholder="La tua nuova password"
            className="pr-10"
            {...register("new_password")}
          />
          <button
            type="button"
            onClick={() => setShowPassword((v) => !v)}
            className="absolute right-3 top-1/2 -translate-y-1/2 text-gray-400 hover:text-gray-600"
          >
            {showPassword ? <EyeOff className="h-4 w-4" /> : <Eye className="h-4 w-4" />}
          </button>
        </div>
        {errors.new_password && (
          <p className="text-xs text-red-500">{errors.new_password.message}</p>
        )}

        {/* Password strength indicators */}
        {password && (
          <ul className="mt-2 space-y-1">
            {PASSWORD_REQUIREMENTS.map((req) => (
              <li
                key={req.label}
                className={`flex items-center gap-2 text-xs ${
                  req.test(password) ? "text-green-600" : "text-gray-400"
                }`}
              >
                <span className="w-3 h-3 rounded-full border flex-shrink-0 flex items-center justify-center
                  ${req.test(password) ? 'border-green-600 bg-green-600' : 'border-gray-300'}">
                  {req.test(password) && <CheckCircle2 className="h-3 w-3" />}
                </span>
                {req.label}
              </li>
            ))}
          </ul>
        )}
      </div>

      <div className="space-y-1">
        <Label htmlFor="confirm_password">Conferma password</Label>
        <Input
          id="confirm_password"
          type={showPassword ? "text" : "password"}
          placeholder="Ripeti la password"
          {...register("confirm_password")}
        />
        {errors.confirm_password && (
          <p className="text-xs text-red-500">{errors.confirm_password.message}</p>
        )}
      </div>

      <Button type="submit" className="w-full" disabled={isSubmitting}>
        {isSubmitting ? (
          <>
            <Loader2 className="mr-2 h-4 w-4 animate-spin" />
            Salvataggio…
          </>
        ) : (
          "Imposta nuova password"
        )}
      </Button>
    </form>
  );
}
