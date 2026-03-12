import type { Metadata } from "next";
import Link from "next/link";
import { Scissors, Briefcase, ArrowRight } from "lucide-react";
import { Card, CardContent } from "@/components/ui/card";

export const metadata: Metadata = {
  title: "Registrati",
  description: "Scegli come vuoi registrarti su HairMatch",
};

export default function RegisterPage() {
  return (
    <div className="w-full max-w-lg">
      <div className="mb-8 text-center">
        <h1 className="text-3xl font-bold text-gray-900">Crea il tuo account</h1>
        <p className="mt-2 text-gray-600">
          Seleziona il tipo di account che desideri creare
        </p>
      </div>

      <div className="grid gap-4 sm:grid-cols-2">
        {/* Salon Card */}
        <Link href="/register/salon" className="group block">
          <Card className="h-full cursor-pointer border-2 border-transparent transition-all hover:border-indigo-500 hover:shadow-md group-focus-within:border-indigo-500">
            <CardContent className="flex flex-col items-center p-6 text-center">
              <div className="mb-4 inline-flex h-16 w-16 items-center justify-center rounded-2xl bg-indigo-100 transition-colors group-hover:bg-indigo-200">
                <Scissors className="h-8 w-8 text-indigo-600" />
              </div>
              <h2 className="mb-2 text-lg font-semibold text-gray-900">
                Salone
              </h2>
              <p className="mb-4 text-sm text-gray-600">
                Gestisci il tuo salone, pubblica annunci e trova i migliori
                professionisti per il tuo team.
              </p>
              <div className="flex items-center gap-1 text-sm font-medium text-indigo-600">
                Inizia ora
                <ArrowRight className="h-4 w-4 transition-transform group-hover:translate-x-1" />
              </div>
            </CardContent>
          </Card>
        </Link>

        {/* Professional Card */}
        <Link href="/register/professional" className="group block">
          <Card className="h-full cursor-pointer border-2 border-transparent transition-all hover:border-violet-500 hover:shadow-md group-focus-within:border-violet-500">
            <CardContent className="flex flex-col items-center p-6 text-center">
              <div className="mb-4 inline-flex h-16 w-16 items-center justify-center rounded-2xl bg-violet-100 transition-colors group-hover:bg-violet-200">
                <Briefcase className="h-8 w-8 text-violet-600" />
              </div>
              <h2 className="mb-2 text-lg font-semibold text-gray-900">
                Professionista
              </h2>
              <p className="mb-4 text-sm text-gray-600">
                Mostra le tue specializzazioni, candidati ai saloni e trova
                le migliori opportunità per la tua carriera.
              </p>
              <div className="flex items-center gap-1 text-sm font-medium text-violet-600">
                Inizia ora
                <ArrowRight className="h-4 w-4 transition-transform group-hover:translate-x-1" />
              </div>
            </CardContent>
          </Card>
        </Link>
      </div>

      <p className="mt-6 text-center text-sm text-gray-600">
        Hai già un account?{" "}
        <Link href="/login" className="font-medium text-indigo-600 hover:underline">
          Accedi
        </Link>
      </p>
    </div>
  );
}
