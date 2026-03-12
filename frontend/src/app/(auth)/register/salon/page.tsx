import type { Metadata } from "next";
import Link from "next/link";
import { ChevronLeft } from "lucide-react";
import { SalonRegisterForm } from "@/components/auth/SalonRegisterForm";
import {
  Card,
  CardHeader,
  CardTitle,
  CardDescription,
  CardContent,
} from "@/components/ui/card";

export const metadata: Metadata = {
  title: "Registra il tuo Salone",
  description: "Crea un account salone su HairMatch",
};

export default function SalonRegisterPage() {
  return (
    <div className="w-full max-w-xl">
      <Link
        href="/register"
        className="mb-4 inline-flex items-center gap-1 text-sm text-gray-600 hover:text-gray-900"
      >
        <ChevronLeft className="h-4 w-4" />
        Torna alla scelta ruolo
      </Link>

      <Card className="shadow-lg">
        <CardHeader className="text-center">
          <CardTitle className="text-2xl font-bold">Registra il Salone</CardTitle>
          <CardDescription>
            Crea il profilo del tuo salone su HairMatch
          </CardDescription>
        </CardHeader>
        <CardContent>
          <SalonRegisterForm />
        </CardContent>
      </Card>
    </div>
  );
}
