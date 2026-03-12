"use client";

import { useEffect } from "react";
import { useRouter } from "next/navigation";
import { Loader2 } from "lucide-react";
import { useAuth } from "@/hooks/useAuth";

/**
 * Intermediate page used by middleware to redirect authenticated users
 * to the correct dashboard based on their role.
 * This page reads the role from the Zustand store (populated after hydration).
 */
export default function DashboardRedirectPage() {
  const { user, isLoading, isAuthenticated } = useAuth();
  const router = useRouter();

  useEffect(() => {
    if (isLoading) return;

    if (!isAuthenticated || !user) {
      router.replace("/login");
      return;
    }

    if (user.role === "salon") {
      router.replace("/dashboard/salon");
    } else if (user.role === "professional") {
      router.replace("/dashboard/professional");
    } else {
      router.replace("/");
    }
  }, [user, isLoading, isAuthenticated, router]);

  return (
    <div className="flex min-h-screen items-center justify-center">
      <div className="flex flex-col items-center gap-3">
        <Loader2 className="h-8 w-8 animate-spin text-indigo-600" />
        <p className="text-sm text-gray-600">Caricamento dashboard…</p>
      </div>
    </div>
  );
}
