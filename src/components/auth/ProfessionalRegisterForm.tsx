"use client";

import { useState } from "react";
import { useForm } from "react-hook-form";
import { zodResolver } from "@hookform/resolvers/zod";
import { z } from "zod";
import { useRouter } from "next/navigation";
import { Loader2, Eye, EyeOff, Check, X } from "lucide-react";

import { apiRegisterProfessional } from "@/lib/api/auth";
import { ApiRequestError } from "@/lib/api/auth";
import { SPECIALIZATIONS, ITALIAN_PROVINCES } from "@/types/auth";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import {
  Form,
  FormControl,
  FormField,
  FormItem,
  FormLabel,
  FormMessage,
  FormDescription,
} from "@/components/ui/form";
import { Alert, AlertDescription } from "@/components/ui/alert";
import { cn } from "@/lib/utils";

const passwordSchema = z
  .string()
  .min(8, "Minimo 8 caratteri")
  .regex(/[A-Z]/, "Almeno una lettera maiuscola")
  .regex(/[0-9]/, "Almeno un numero")
  .regex(/[^A-Za-z0-9]/, "Almeno un carattere speciale");

const phoneSchema = z
  .string()
  .regex(/^\+?[0-9\s\-\(\)]{7,20}$/, "Numero di telefono non valido");

const professionalRegisterSchema = z
  .object({
    email: z.string().email("Inserisci un'email valida"),
    password: passwordSchema,
    confirmPassword: z.string(),
    first_name: z.string().min(2, "Il nome è obbligatorio"),
    last_name: z.string().min(2, "Il cognome è obbligatorio"),
    phone: phoneSchema,
    specializations: z
      .array(z.string())
      .min(1, "Seleziona almeno una specializzazione"),
    years_of_experience: z
      .number({ invalid_type_error: "Inserisci un numero valido" })
      .int()
      .min(0, "Minimo 0 anni")
      .max(60, "Massimo 60 anni")
      .optional()
      .or(z.literal(undefined)),
    preferred_city: z.string().optional(),
    preferred_province: z
      .string()
      .refine(
        (v) => !v || (ITALIAN_PROVINCES as readonly string[]).includes(v),
        "Provincia non valida"
      )
      .optional(),
  })
  .refine((data) => data.password === data.confirmPassword, {
    message: "Le password non coincidono",
    path: ["confirmPassword"],
  });

type ProfessionalRegisterFormValues = z.infer<typeof professionalRegisterSchema>;

function PasswordStrength({ password }: { password: string }) {
  const checks = [
    { label: "8+ caratteri", ok: password.length >= 8 },
    { label: "Maiuscola", ok: /[A-Z]/.test(password) },
    { label: "Numero", ok: /[0-9]/.test(password) },
    { label: "Carattere speciale", ok: /[^A-Za-z0-9]/.test(password) },
  ];
  const passed = checks.filter((c) => c.ok).length;
  const strength =
    passed === 0
      ? "none"
      : passed <= 2
      ? "weak"
      : passed === 3
      ? "medium"
      : "strong";

  if (!password) return null;

  return (
    <div className="mt-1 space-y-1">
      <div className="flex gap-1">
        {[1, 2, 3, 4].map((i) => (
          <div
            key={i}
            className={cn(
              "h-1 flex-1 rounded-full transition-colors",
              strength === "none"
                ? "bg-muted"
                : strength === "weak" && i <= 1
                ? "bg-red-500"
                : strength === "medium" && i <= 3
                ? "bg-yellow-500"
                : strength === "strong"
                ? "bg-green-500"
                : "bg-muted"
            )}
          />
        ))}
      </div>
      <div className="flex flex-wrap gap-x-3 gap-y-0.5">
        {checks.map((c) => (
          <span
            key={c.label}
            className={cn(
              "flex items-center gap-1 text-xs",
              c.ok ? "text-green-600" : "text-muted-foreground"
            )}
          >
            {c.ok && <Check className="h-3 w-3" />}
            {c.label}
          </span>
        ))}
      </div>
    </div>
  );
}

function SpecializationsSelector({
  value,
  onChange,
  error,
}: {
  value: string[];
  onChange: (v: string[]) => void;
  error?: string;
}) {
  const toggle = (spec: string) => {
    if (value.includes(spec)) {
      onChange(value.filter((s) => s !== spec));
    } else {
      onChange([...value, spec]);
    }
  };

  return (
    <div className="space-y-2">
      <div className="flex flex-wrap gap-2">
        {SPECIALIZATIONS.map((spec) => {
          const selected = value.includes(spec);
          return (
            <button
              key={spec}
              type="button"
              onClick={() => toggle(spec)}
              className={cn(
                "inline-flex items-center gap-1 rounded-full border px-3 py-1 text-sm font-medium transition-colors",
                selected
                  ? "border-violet-500 bg-violet-100 text-violet-700"
                  : "border-input bg-background text-foreground hover:bg-accent"
              )}
              aria-pressed={selected}
            >
              {selected && <Check className="h-3 w-3" />}
              {spec}
            </button>
          );
        })}
      </div>
      {value.length > 0 && (
        <div className="flex flex-wrap gap-1">
          {value.map((spec) => (
            <span
              key={spec}
              className="inline-flex items-center gap-1 rounded bg-violet-100 px-2 py-0.5 text-xs text-violet-700"
            >
              {spec}
              <button
                type="button"
                onClick={() => toggle(spec)}
                className="hover:text-violet-900"
                aria-label={`Rimuovi ${spec}`}
              >
                <X className="h-3 w-3" />
              </button>
            </span>
          ))}
        </div>
      )}
      {error && <p className="text-sm font-medium text-destructive">{error}</p>}
    </div>
  );
}

export function ProfessionalRegisterForm() {
  const router = useRouter();
  const [errorMessage, setErrorMessage] = useState<string>("");
  const [showPassword, setShowPassword] = useState(false);
  const [showConfirm, setShowConfirm] = useState(false);

  const form = useForm<ProfessionalRegisterFormValues>({
    resolver: zodResolver(professionalRegisterSchema),
    defaultValues: {
      email: "",
      password: "",
      confirmPassword: "",
      first_name: "",
      last_name: "",
      phone: "",
      specializations: [],
      years_of_experience: undefined,
      preferred_city: "",
      preferred_province: "",
    },
  });

  const watchedPassword = form.watch("password");

  const onSubmit = async (values: ProfessionalRegisterFormValues) => {
    setErrorMessage("");

    try {
      await apiRegisterProfessional({
        email: values.email,
        password: values.password,
        first_name: values.first_name,
        last_name: values.last_name,
        phone: values.phone,
        specializations: values.specializations,
        years_of_experience: values.years_of_experience,
        preferred_city: values.preferred_city || undefined,
        preferred_province: values.preferred_province || undefined,
      });
      router.push(`/register/professional/confirm?email=${encodeURIComponent(values.email)}`);
    } catch (err) {
      if (err instanceof ApiRequestError) {
        if (err.statusCode === 409) {
          const msg = err.message.toLowerCase();
          if (msg.includes("email")) {
            form.setError("email", {
              message: "Questa email è già registrata.",
            });
          } else {
            setErrorMessage(err.message);
          }
        } else if (err.statusCode === 422) {
          setErrorMessage("Verifica i campi inseriti e riprova.");
        } else {
          setErrorMessage(err.message);
        }
      } else {
        setErrorMessage("Si è verificato un errore imprevisto. Riprova.");
      }
    }
  };

  return (
    <Form {...form}>
      <form onSubmit={form.handleSubmit(onSubmit)} className="space-y-5" noValidate>
        {errorMessage && (
          <Alert variant="destructive">
            <AlertDescription>{errorMessage}</AlertDescription>
          </Alert>
        )}

        {/* Email */}
        <FormField
          control={form.control}
          name="email"
          render={({ field }) => (
            <FormItem>
              <FormLabel>Email *</FormLabel>
              <FormControl>
                <Input
                  type="email"
                  placeholder="nome@esempio.it"
                  autoComplete="email"
                  {...field}
                />
              </FormControl>
              <FormMessage />
            </FormItem>
          )}
        />

        {/* Password */}
        <FormField
          control={form.control}
          name="password"
          render={({ field }) => (
            <FormItem>
              <FormLabel>Password *</FormLabel>
              <FormControl>
                <div className="relative">
                  <Input
                    type={showPassword ? "text" : "password"}
                    placeholder="Crea una password sicura"
                    autoComplete="new-password"
                    className="pr-10"
                    {...field}
                  />
                  <button
                    type="button"
                    onClick={() => setShowPassword((v) => !v)}
                    className="absolute right-3 top-1/2 -translate-y-1/2 text-muted-foreground hover:text-foreground"
                    aria-label={showPassword ? "Nascondi password" : "Mostra password"}
                  >
                    {showPassword ? (
                      <EyeOff className="h-4 w-4" />
                    ) : (
                      <Eye className="h-4 w-4" />
                    )}
                  </button>
                </div>
              </FormControl>
              <PasswordStrength password={watchedPassword} />
              <FormMessage />
            </FormItem>
          )}
        />

        {/* Confirm password */}
        <FormField
          control={form.control}
          name="confirmPassword"
          render={({ field }) => (
            <FormItem>
              <FormLabel>Conferma password *</FormLabel>
              <FormControl>
                <div className="relative">
                  <Input
                    type={showConfirm ? "text" : "password"}
                    placeholder="Ripeti la password"
                    autoComplete="new-password"
                    className="pr-10"
                    {...field}
                  />
                  <button
                    type="button"
                    onClick={() => setShowConfirm((v) => !v)}
                    className="absolute right-3 top-1/2 -translate-y-1/2 text-muted-foreground hover:text-foreground"
                    aria-label={showConfirm ? "Nascondi password" : "Mostra password"}
                  >
                    {showConfirm ? (
                      <EyeOff className="h-4 w-4" />
                    ) : (
                      <Eye className="h-4 w-4" />
                    )}
                  </button>
                </div>
              </FormControl>
              <FormMessage />
            </FormItem>
          )}
        />

        <div className="border-t pt-4">
          <p className="mb-4 text-sm font-medium text-muted-foreground">
            Informazioni personali
          </p>
          <div className="space-y-5">
            <div className="grid grid-cols-2 gap-4">
              <FormField
                control={form.control}
                name="first_name"
                render={({ field }) => (
                  <FormItem>
                    <FormLabel>Nome *</FormLabel>
                    <FormControl>
                      <Input
                        placeholder="Mario"
                        autoComplete="given-name"
                        {...field}
                      />
                    </FormControl>
                    <FormMessage />
                  </FormItem>
                )}
              />
              <FormField
                control={form.control}
                name="last_name"
                render={({ field }) => (
                  <FormItem>
                    <FormLabel>Cognome *</FormLabel>
                    <FormControl>
                      <Input
                        placeholder="Rossi"
                        autoComplete="family-name"
                        {...field}
                      />
                    </FormControl>
                    <FormMessage />
                  </FormItem>
                )}
              />
            </div>

            <FormField
              control={form.control}
              name="phone"
              render={({ field }) => (
                <FormItem>
                  <FormLabel>Telefono *</FormLabel>
                  <FormControl>
                    <Input
                      type="tel"
                      placeholder="+39 333 1234567"
                      autoComplete="tel"
                      {...field}
                    />
                  </FormControl>
                  <FormMessage />
                </FormItem>
              )}
            />

            {/* Specializations */}
            <FormField
              control={form.control}
              name="specializations"
              render={({ field }) => (
                <FormItem>
                  <FormLabel>Specializzazioni *</FormLabel>
                  <FormDescription>
                    Seleziona le tue specializzazioni (almeno una)
                  </FormDescription>
                  <FormControl>
                    <SpecializationsSelector
                      value={field.value}
                      onChange={field.onChange}
                      error={form.formState.errors.specializations?.message}
                    />
                  </FormControl>
                </FormItem>
              )}
            />
          </div>
        </div>

        <div className="border-t pt-4">
          <p className="mb-4 text-sm font-medium text-muted-foreground">
            Informazioni facoltative
          </p>
          <div className="space-y-5">
            <FormField
              control={form.control}
              name="years_of_experience"
              render={({ field }) => (
                <FormItem>
                  <FormLabel>Anni di esperienza</FormLabel>
                  <FormControl>
                    <Input
                      type="number"
                      placeholder="5"
                      min={0}
                      max={60}
                      {...field}
                      value={field.value ?? ""}
                      onChange={(e) => {
                        const val = e.target.value;
                        field.onChange(
                          val === "" ? undefined : parseInt(val, 10)
                        );
                      }}
                    />
                  </FormControl>
                  <FormMessage />
                </FormItem>
              )}
            />

            <div className="grid grid-cols-2 gap-4">
              <FormField
                control={form.control}
                name="preferred_city"
                render={({ field }) => (
                  <FormItem>
                    <FormLabel>Città preferita</FormLabel>
                    <FormControl>
                      <Input placeholder="Milano" {...field} />
                    </FormControl>
                    <FormMessage />
                  </FormItem>
                )}
              />
              <FormField
                control={form.control}
                name="preferred_province"
                render={({ field }) => (
                  <FormItem>
                    <FormLabel>Provincia preferita</FormLabel>
                    <FormControl>
                      <select
                        className="flex h-10 w-full rounded-md border border-input bg-background px-3 py-2 text-sm ring-offset-background focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring focus-visible:ring-offset-2 disabled:cursor-not-allowed disabled:opacity-50"
                        {...field}
                      >
                        <option value="">--</option>
                        {ITALIAN_PROVINCES.map((p) => (
                          <option key={p} value={p}>
                            {p}
                          </option>
                        ))}
                      </select>
                    </FormControl>
                    <FormMessage />
                  </FormItem>
                )}
              />
            </div>
          </div>
        </div>

        <Button
          type="submit"
          className="w-full bg-violet-600 hover:bg-violet-700"
          disabled={form.formState.isSubmitting}
        >
          {form.formState.isSubmitting ? (
            <>
              <Loader2 className="mr-2 h-4 w-4 animate-spin" />
              Registrazione in corso…
            </>
          ) : (
            "Crea account professionista"
          )}
        </Button>
      </form>
    </Form>
  );
}
