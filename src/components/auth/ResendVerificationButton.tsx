"use client";

import { useState } from "react";
import { Loader2, RefreshCw, CheckCircle2 } from "lucide-react";
import { Button } from "@/components/ui/button";
import { apiResendVerification } from "@/lib/api/auth";

interface ResendVerificationButtonProps {
  email: string | null;
  accentColor?: "indigo" | "violet";
}

export function ResendVerificationButton({
  email,
  accentColor = "indigo",
}: ResendVerificationButtonProps) {
  const [status, setStatus] = useState<"idle" | "loading" | "sent" | "error">("idle");
  const [countdown, setCountdown] = useState(0);

  const colorClass =
    accentColor === "violet"
      ? "text-violet-600 hover:text-violet-700"
      : "text-indigo-600 hover:text-indigo-700";

  const startCountdown = () => {
    setCountdown(60);
    const interval = setInterval(() => {
      setCountdown((c) => {
        if (c <= 1) {
          clearInterval(interval);
          return 0;
        }
        return c - 1;
      });
    }, 1000);
  };

  const handleResend = async () => {
    if (!email || countdown > 0) return;

    setStatus("loading");
    try {
      await apiResendVerification(email);
      setStatus("sent");
      startCountdown();
    } catch {
      setStatus("error");
      setTimeout(() => setStatus("idle"), 3000);
    }
  };

  if (status === "sent") {
    return (
      <div className="mt-4 flex items-center justify-center gap-2 text-green-600 text-sm">
        <CheckCircle2 className="h-4 w-4" />
        <span>Email inviata! Controlla la tua casella.</span>
      </div>
    );
  }

  if (status === "error") {
    return (
      <p className="mt-4 text-sm text-red-500 text-center">
        Errore nell&apos;invio. Riprova tra qualche minuto.
      </p>
    );
  }

  return (
    <div className="mt-4 text-center">
      <Button
        variant="ghost"
        size="sm"
        onClick={handleResend}
        disabled={status === "loading" || countdown > 0}
        className={`text-sm ${colorClass} disabled:opacity-50`}
      >
        {status === "loading" ? (
          <>
            <Loader2 className="mr-2 h-3 w-3 animate-spin" />
            Invio in corso…
          </>
        ) : countdown > 0 ? (
          <>
            <RefreshCw className="mr-2 h-3 w-3" />
            Reinvia tra {countdown}s
          </>
        ) : (
          <>
            <RefreshCw className="mr-2 h-3 w-3" />
            Non hai ricevuto l&apos;email? Reinvia
          </>
        )}
      </Button>
    </div>
  );
}
