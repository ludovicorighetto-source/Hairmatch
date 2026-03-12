"use client";

import { useState } from "react";
import { useForm } from "react-hook-form";
import { zodResolver } from "@hookform/resolvers/zod";
import { z } from "zod";
import { useRouter } from "next/navigation";
import { Loader2, Eye, EyeOff, Check } from "lucide-react";

import { apiRegisterSalon } from "@/lib/api/auth";
import { ApiRequestError } from "@/lib/api/auth";
import { ITALIAN_PROVINCES } from "@/types/auth";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import {
  Form,
  FormControl,
  FormField,
  FormItem,
  FormLabel,
  FormMessage,
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

const vatSchema = z
  .string()
  .regex(/^[0-9]{11}$/, "Partita IVA non valida (11 cifre)");

const salonRegisterSchema = z
  .object({
    email: z.string().email("Inserisci un'email valida"),
    password: passwordSchema,
    confirmPassword: z.string(),
    business_name: z.string().min(2, "Il nome del salone è obbligatorio"),
    phone: phoneSchema,
    street: z.string().min(3, "Inserisci una via valida"),
    city: z.string().min(2, "Inserisci una città valida"),
    province: z
      .string()
      .length(2, "Seleziona una provincia")
      .refine(
        (v) => (ITALIAN_PROVINCES as readonly string[]).includes(v),
        "Provincia non valida"
      ),
    postal_code: z
      .string()
      .regex(/^[0-9]{5}$/, "Il CAP deve essere di 5 cifre"),
    vat_number: z
      .union([vatSchema, z.literal("")])
      .optional(),
    website: z
      .string()
      .url("Inserisci un URL valido (es. https://esempio.it)")
      .optional()
      .or(z.literal("")),
  })
  .refine((data) => data.password === data.confirmPassword, {
    message: "Le password non coincidono",
    path: ["confirmPassword"],
  });

type SalonRegisterFormValues = z.infer<typeof salonRegisterSchema>;

// Password strength indicator
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

export function SalonRegisterForm() {
  const router = useRouter();
  const [errorMessage, setErrorMessage] = useState<string>("");
  const [showPassword, setShowPassword] = useState(false);
  const [showConfirm, setShowConfirm] = useState(false);

  const form = useForm<SalonRegisterFormValues>({
    resolver: zodResolver(salonRegisterSchema),
    defaultValues: {
      email: "",
      password: "",
      confirmPassword: "",
      business_name: "",
      phone: "",
      street: "",
      city: "",
      province: "",
      postal_code: "",
      vat_number: "",
      website: "",
    },
  });

  const watchedPassword = form.watch("password");

  const onSubmit = async (values: SalonRegisterFormValues) => {
    setErrorMessage("");

    try {
      await apiRegisterSalon({
        email: values.email,
        password: values.password,
        business_name: values.business_name,
        phone: values.phone,
        address: {
          street: values.street,
          city: values.city,
          province: values.province,
          postal_code: values.postal_code,
        },
        vat_number: values.vat_number || undefined,
        website: values.website || undefined,
      });
      router.push("/register/salon/confirm");
    } catch (err) {
      if (err instanceof ApiRequestError) {
        if (err.statusCode === 409) {
          const msg = err.message.toLowerCase();
          if (msg.includes("email")) {
            form.setError("email", {
              message: "Questa email è già registrata.",
            });
          } else if (msg.includes("iva") || msg.includes("vat")) {
            form.setError("vat_number", {
              message: "Questa Partita IVA è già registrata.",
            });
          } else {
            setErrorMessage(err.message);
          }
        } else if (err.statusCode === 422) {
          setErrorMessage(
            "Verifica i campi inseriti e riprova."
          );
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
                  placeholder="salone@esempio.it"
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
            Informazioni salone
          </p>

          {/* Business name */}
          <div className="space-y-5">
            <FormField
              control={form.control}
              name="business_name"
              render={({ field }) => (
                <FormItem>
                  <FormLabel>Nome Salone *</FormLabel>
                  <FormControl>
                    <Input placeholder="Il tuo salone" {...field} />
                  </FormControl>
                  <FormMessage />
                </FormItem>
              )}
            />

            {/* Phone */}
            <FormField
              control={form.control}
              name="phone"
              render={({ field }) => (
                <FormItem>
                  <FormLabel>Telefono *</FormLabel>
                  <FormControl>
                    <Input
                      type="tel"
                      placeholder="+39 02 1234567"
                      autoComplete="tel"
                      {...field}
                    />
                  </FormControl>
                  <FormMessage />
                </FormItem>
              )}
            />

            {/* Street */}
            <FormField
              control={form.control}
              name="street"
              render={({ field }) => (
                <FormItem>
                  <FormLabel>Via *</FormLabel>
                  <FormControl>
                    <Input placeholder="Via Roma 1" {...field} />
                  </FormControl>
                  <FormMessage />
                </FormItem>
              )}
            />

            {/* City + Province */}
            <div className="grid grid-cols-2 gap-4">
              <FormField
                control={form.control}
                name="city"
                render={({ field }) => (
                  <FormItem>
                    <FormLabel>Città *</FormLabel>
                    <FormControl>
                      <Input placeholder="Milano" {...field} />
                    </FormControl>
                    <FormMessage />
                  </FormItem>
                )}
              />
              <FormField
                control={form.control}
                name="province"
                render={({ field }) => (
                  <FormItem>
                    <FormLabel>Provincia *</FormLabel>
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

            {/* Postal code */}
            <FormField
              control={form.control}
              name="postal_code"
              render={({ field }) => (
                <FormItem>
                  <FormLabel>CAP *</FormLabel>
                  <FormControl>
                    <Input
                      placeholder="20100"
                      maxLength={5}
                      {...field}
                    />
                  </FormControl>
                  <FormMessage />
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
            {/* VAT number */}
            <FormField
              control={form.control}
              name="vat_number"
              render={({ field }) => (
                <FormItem>
                  <FormLabel>Partita IVA</FormLabel>
                  <FormControl>
                    <Input
                      placeholder="12345678901"
                      maxLength={11}
                      {...field}
                    />
                  </FormControl>
                  <FormMessage />
                </FormItem>
              )}
            />

            {/* Website */}
            <FormField
              control={form.control}
              name="website"
              render={({ field }) => (
                <FormItem>
                  <FormLabel>Sito web</FormLabel>
                  <FormControl>
                    <Input
                      type="url"
                      placeholder="https://www.tuosalone.it"
                      {...field}
                    />
                  </FormControl>
                  <FormMessage />
                </FormItem>
              )}
            />
          </div>
        </div>

        <Button
          type="submit"
          className="w-full bg-indigo-600 hover:bg-indigo-700"
          disabled={form.formState.isSubmitting}
        >
          {form.formState.isSubmitting ? (
            <>
              <Loader2 className="mr-2 h-4 w-4 animate-spin" />
              Registrazione in corso…
            </>
          ) : (
            "Crea account salone"
          )}
        </Button>
      </form>
    </Form>
  );
}
