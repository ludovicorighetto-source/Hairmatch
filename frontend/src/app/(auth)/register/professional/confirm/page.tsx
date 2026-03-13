import type { Metadata } from "next";
import Link from "next/link";
import { Mail, CheckCircle } from "lucide-react";
import { Button } from "@/components/ui/button";
import { Card, CardContent } from "@/components/ui/card";
import { ResendVerificationButton } from "@/components/auth/ResendVerificationButton";

export const metadata: Metadata = {
  title: "Controlla la tua email — Professionista",
  description: "Conferma il tuo indirizzo email per completare la registrazione",
};

interface Props {
  searchParams: Promise<{ email?: string }>;
}

export default async function ProfessionalConfirmPage({ searchParams }: Props) {
  const { email } = await searchParams;

  return (
    <div className="w-full max-w-md">
      <Card className="shadow-lg">
        <CardContent className="p-8 text-center">
          <div className="mx-auto mb-6 flex h-20 w-20 items-center justify-center rounded-full bg-violet-100">
            <Mail className="h-10 w-10 text-violet-600" />
          </div>

          <div className="mb-4 flex items-center justify-center gap-2 text-green-600">
            <CheckCircle className="h-5 w-5" />
            <span className="text-sm font-medium">Registrazione completata</span>
          </div>

          <h1 className="mb-3 text-2xl font-bold text-gray-900">
            Controlla la tua email
          </h1>

          {email && (
            <p className="mb-2 text-sm font-medium text-violet-600">{email}</p>
          )}

          <p className="mb-2 text-gray-600">
            Ti abbiamo inviato un&apos;email di conferma.
          </p>
          <p className="mb-6 text-sm text-gray-500">
            Clicca sul link nell&apos;email per verificare il tuo account e iniziare
            a usare HairMatch come professionista. Controlla anche la cartella
            spam se non vedi il messaggio.
          </p>

          <Link href="/login">
            <Button className="w-full bg-violet-600 hover:bg-violet-700">
              Vai al login
            </Button>
          </Link>

          <ResendVerificationButton email={email ?? null} accentColor="violet" />
        </CardContent>
      </Card>
    </div>
  );
}
