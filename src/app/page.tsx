import Link from "next/link";
import { Scissors, Briefcase, Star, Users, ArrowRight } from "lucide-react";
import { Button } from "@/components/ui/button";
import { Card, CardContent } from "@/components/ui/card";

export default function HomePage() {
  return (
    <main className="min-h-screen bg-gradient-to-br from-indigo-50 via-white to-violet-50">
      {/* Navigation */}
      <nav className="border-b bg-white/80 backdrop-blur-sm">
        <div className="mx-auto flex max-w-6xl items-center justify-between px-4 py-4">
          <div className="flex items-center gap-2">
            <Scissors className="h-6 w-6 text-indigo-600" />
            <span className="text-xl font-bold text-gray-900">HairMatch</span>
          </div>
          <Link href="/login">
            <Button variant="outline" size="sm">
              Accedi
            </Button>
          </Link>
        </div>
      </nav>

      {/* Hero Section */}
      <section className="mx-auto max-w-6xl px-4 py-16 sm:py-24">
        <div className="text-center">
          <div className="mb-4 inline-flex items-center rounded-full bg-indigo-100 px-4 py-1.5 text-sm font-medium text-indigo-700">
            <Star className="mr-1.5 h-3.5 w-3.5" />
            La piattaforma #1 per il mondo dei capelli
          </div>
          <h1 className="mt-4 text-4xl font-bold tracking-tight text-gray-900 sm:text-5xl lg:text-6xl">
            Connetti il tuo{" "}
            <span className="bg-gradient-to-r from-indigo-600 to-violet-600 bg-clip-text text-transparent">
              talento
            </span>{" "}
            con le opportunità
          </h1>
          <p className="mx-auto mt-6 max-w-2xl text-lg text-gray-600">
            HairMatch mette in contatto i migliori saloni di bellezza con
            professionisti qualificati. Trova il match perfetto in pochi minuti.
          </p>

          {/* CTA Buttons */}
          <div className="mt-10 flex flex-col items-center gap-4 sm:flex-row sm:justify-center">
            <Link href="/register/salon">
              <Button
                size="lg"
                className="w-full gap-2 bg-indigo-600 hover:bg-indigo-700 sm:w-auto"
              >
                <Scissors className="h-5 w-5" />
                Sei un salone?
                <ArrowRight className="h-4 w-4" />
              </Button>
            </Link>
            <Link href="/register/professional">
              <Button
                size="lg"
                variant="outline"
                className="w-full gap-2 border-violet-500 text-violet-700 hover:bg-violet-50 sm:w-auto"
              >
                <Briefcase className="h-5 w-5" />
                Sei un professionista?
                <ArrowRight className="h-4 w-4" />
              </Button>
            </Link>
          </div>

          <p className="mt-4 text-sm text-gray-500">
            Hai già un account?{" "}
            <Link
              href="/login"
              className="font-medium text-indigo-600 hover:underline"
            >
              Accedi
            </Link>
          </p>
        </div>
      </section>

      {/* Feature Cards */}
      <section className="mx-auto max-w-6xl px-4 pb-16">
        <div className="grid gap-6 sm:grid-cols-2 lg:grid-cols-3">
          <Card className="border-indigo-100 bg-white/70 backdrop-blur-sm">
            <CardContent className="p-6">
              <div className="mb-4 inline-flex h-12 w-12 items-center justify-center rounded-xl bg-indigo-100">
                <Scissors className="h-6 w-6 text-indigo-600" />
              </div>
              <h3 className="mb-2 text-lg font-semibold text-gray-900">
                Per i Saloni
              </h3>
              <p className="text-sm text-gray-600">
                Pubblica annunci, trova professionisti qualificati e gestisci
                tutto dalla tua dashboard personalizzata.
              </p>
            </CardContent>
          </Card>

          <Card className="border-violet-100 bg-white/70 backdrop-blur-sm">
            <CardContent className="p-6">
              <div className="mb-4 inline-flex h-12 w-12 items-center justify-center rounded-xl bg-violet-100">
                <Briefcase className="h-6 w-6 text-violet-600" />
              </div>
              <h3 className="mb-2 text-lg font-semibold text-gray-900">
                Per i Professionisti
              </h3>
              <p className="text-sm text-gray-600">
                Mostra le tue specializzazioni, candidati alle offerte e trova
                il salone ideale per la tua crescita professionale.
              </p>
            </CardContent>
          </Card>

          <Card className="border-gray-100 bg-white/70 backdrop-blur-sm sm:col-span-2 lg:col-span-1">
            <CardContent className="p-6">
              <div className="mb-4 inline-flex h-12 w-12 items-center justify-center rounded-xl bg-green-100">
                <Users className="h-6 w-6 text-green-600" />
              </div>
              <h3 className="mb-2 text-lg font-semibold text-gray-900">
                Match Perfetti
              </h3>
              <p className="text-sm text-gray-600">
                Il nostro algoritmo abbina saloni e professionisti in base a
                specializzazioni, zona geografica e disponibilità.
              </p>
            </CardContent>
          </Card>
        </div>
      </section>

      {/* Footer */}
      <footer className="border-t bg-white py-8">
        <div className="mx-auto max-w-6xl px-4 text-center text-sm text-gray-500">
          <p>© {new Date().getFullYear()} HairMatch. Tutti i diritti riservati.</p>
        </div>
      </footer>
    </main>
  );
}
