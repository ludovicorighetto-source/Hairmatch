import type { Metadata } from "next";
import Link from "next/link";
import { ChevronLeft } from "lucide-react";
import { ProfessionalRegisterForm } from "@/components/auth/ProfessionalRegisterForm";
import {
  Card,
  CardHeader,
  CardTitle,
  CardDescription,
  CardContent,
} from "@/components/ui/card";

export const metadata: Metadata = {
  title: "Registrati come Professionista",
  description: "Crea un account professionista su HairMatch",
};

export default function ProfessionalRegisterPage() {
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
          <CardTitle className="text-2xl font-bold">
            Registrati come Professionista
          </CardTitle>
          <CardDescription>
            Crea il tuo profilo professionale su HairMatch
          </CardDescription>
        </CardHeader>
        <CardContent>
          <ProfessionalRegisterForm />
        </CardContent>
      </Card>
    </div>
  );
}
