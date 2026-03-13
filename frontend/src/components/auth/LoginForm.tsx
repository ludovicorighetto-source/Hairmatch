"use client";

import { useState } from "react";
import { useForm } from "react-hook-form";
import { zodResolver } from "@hookform/resolvers/zod";
import { z } from "zod";
import { useRouter } from "next/navigation";
import Link from "next/link";
import { Loader2, Eye, EyeOff } from "lucide-react";

import { useAuth } from "@/hooks/useAuth";
import { useAuthStore } from "@/lib/auth/store";
import { apiResendVerification } from "@/lib/api/auth";
import { ApiRequestError } from "@/lib/api/auth";
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

const loginSchema = z.object({
  email: z.string().email("Inserisci un'email valida"),
  password: z.string().min(1, "La password è obbligatoria"),
});

type LoginFormValues = z.infer<typeof loginSchema>;

type ErrorType =
  | "invalid_credentials"
  | "email_not_verified"
  | "account_disabled"
  | "rate_limit"
  | "generic"
  | null;

export function LoginForm() {
  const router = useRouter();
  const { login } = useAuth();
  const [errorType, setErrorType] = useState<ErrorType>(null);
  const [errorMessage, setErrorMessage] = useState<string>("");
  const [showPassword, setShowPassword] = useState(false);
  const [resendEmail, setResendEmail] = useState<string>("");
  const [resendLoading, setResendLoading] = useState(false);
  const [resendSuccess, setResendSuccess] = useState(false);

  const form = useForm<LoginFormValues>({
    resolver: zodResolver(loginSchema),
    defaultValues: {
      email: "",
      password: "",
    },
  });

  const onSubmit = async (values: LoginFormValues) => {
    setErrorType(null);
    setErrorMessage("");
    setResendSuccess(false);

    try {
      await login(values.email, values.password);
      // Role-based redirect based on role from store after login
      const user = useAuthStore.getState().user;
      if (user?.role === "salon") {
        router.push("/dashboard/salon");
      } else if (user?.role === "professional") {
        router.push("/dashboard/professional");
      } else {
        router.push("/");
      }
    } catch (err) {
      if (err instanceof ApiRequestError) {
        if (err.statusCode === 401) {
          setErrorType("invalid_credentials");
          setErrorMessage("Email o password non corretti.");
        } else if (err.statusCode === 403) {
          const msg = err.message.toLowerCase();
          if (msg.includes("verif") || msg.includes("email")) {
            setErrorType("email_not_verified");
            setResendEmail(values.email);
            setErrorMessage(
              "Il tuo account non è ancora verificato. Controlla la tua email."
            );
          } else if (msg.includes("disab") || msg.includes("sospeso")) {
            setErrorType("account_disabled");
            setErrorMessage(
              "Il tuo account è stato disabilitato. Contatta il supporto."
            );
          } else {
            setErrorType("generic");
            setErrorMessage(err.message);
          }
        } else if (err.statusCode === 429) {
          setErrorType("rate_limit");
          setErrorMessage(
            "Troppi tentativi di accesso. Attendi qualche minuto prima di riprovare."
          );
        } else {
          setErrorType("generic");
          setErrorMessage(err.message);
        }
      } else {
        setErrorType("generic");
        setErrorMessage("Si è verificato un errore imprevisto. Riprova.");
      }
    }
  };

  const handleResendVerification = async () => {
    if (!resendEmail) return;
    setResendLoading(true);
    try {
      await apiResendVerification(resendEmail);
      setResendSuccess(true);
    } catch {
      // Best effort
    } finally {
      setResendLoading(false);
    }
  };

  return (
    <Form {...form}>
      <form onSubmit={form.handleSubmit(onSubmit)} className="space-y-5" noValidate>
        {/* General error */}
        {errorType && !resendSuccess && (
          <Alert variant="destructive">
            <AlertDescription>
              <p>{errorMessage}</p>
              {errorType === "email_not_verified" && (
                <Button
                  type="button"
                  variant="link"
                  size="sm"
                  className="mt-1 h-auto p-0 text-destructive underline"
                  onClick={handleResendVerification}
                  disabled={resendLoading}
                >
                  {resendLoading ? (
                    <>
                      <Loader2 className="mr-1 h-3 w-3 animate-spin" />
                      Invio in corso…
                    </>
                  ) : (
                    "Invia di nuovo l'email di verifica"
                  )}
                </Button>
              )}
            </AlertDescription>
          </Alert>
        )}

        {resendSuccess && (
          <Alert variant="success">
            <AlertDescription>
              Email di verifica inviata! Controlla la tua casella di posta.
            </AlertDescription>
          </Alert>
        )}

        <FormField
          control={form.control}
          name="email"
          render={({ field }) => (
            <FormItem>
              <FormLabel>Email</FormLabel>
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

        <FormField
          control={form.control}
          name="password"
          render={({ field }) => (
            <FormItem>
              <FormLabel>Password</FormLabel>
              <FormControl>
                <div className="relative">
                  <Input
                    type={showPassword ? "text" : "password"}
                    placeholder="La tua password"
                    autoComplete="current-password"
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
              <FormMessage />
            </FormItem>
          )}
        />

        <div className="text-right">
          <Link
            href="/request-reset"
            className="text-xs text-indigo-600 hover:underline"
          >
            Password dimenticata?
          </Link>
        </div>

        <Button
          type="submit"
          className="w-full bg-indigo-600 hover:bg-indigo-700"
          disabled={form.formState.isSubmitting}
        >
          {form.formState.isSubmitting ? (
            <>
              <Loader2 className="mr-2 h-4 w-4 animate-spin" />
              Accesso in corso…
            </>
          ) : (
            "Accedi"
          )}
        </Button>

        <div className="flex flex-col gap-2 text-center text-sm text-muted-foreground">
          <p>
            Non hai un account?{" "}
            <Link
              href="/register/salon"
              className="font-medium text-indigo-600 hover:underline"
            >
              Registrati come Salone
            </Link>
          </p>
          <p>
            Sei un professionista?{" "}
            <Link
              href="/register/professional"
              className="font-medium text-violet-600 hover:underline"
            >
              Registrati come Professionista
            </Link>
          </p>
        </div>
      </form>
    </Form>
  );
}
