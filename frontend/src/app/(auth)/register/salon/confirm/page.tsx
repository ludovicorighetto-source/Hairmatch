import type { Metadata } from "next";
import Link from "next/link";
import { Mail, CheckCircle } from "lucide-react";
import { Button } from "@/components/ui/button";
import { Card, CardContent } from "@/components/ui/card";

export const metadata: Metadata = {
  title: "Controlla la tua email — Salone",
  description: "Conferma il tuo indirizzo email per completare la registrazione",
};

export default function SalonConfirmPage() {
  return (
    <div className="w-full max-w-md">
      <Card className="shadow-lg">
        <CardContent className="p-8 text-center">
          {/* Icon */}
          <div className="mx-auto mb-6 flex h-20 w-20 items-center justify-center rounded-full bg-indigo-100">
            <Mail className="h-10 w-10 text-indigo-600" />
          </div>

          {/* Success indicator */}
          <div className="mb-4 flex items-center justify-center gap-2 text-green-600">
            <CheckCircle className="h-5 w-5" />
            <span className="text-sm font-medium">Registrazione completata</span>
          </div>

          <h1 className="mb-3 text-2xl font-bold text-gray-900">
            Controlla la tua email
          </h1>

          <p className="mb-2 text-gray-600">
            Ti abbiamo inviato un'email di conferma.
          </p>
          <p className="mb-6 text-sm text-gray-500">
            Clicca sul link nell'email per verificare il tuo account e iniziare
            a usare HairMatch come salone. Controlla anche la cartella spam se
            non vedi il messaggio.
          </p>

          <Link href="/login">
            <Button className="w-full bg-indigo-600 hover:bg-indigo-700">
              Vai al login
            </Button>
          </Link>

          <p className="mt-4 text-xs text-gray-400">
            Non hai ricevuto l'email? Prova ad accedere e ti chiederemo di
            verificarla di nuovo.
          </p>
        </CardContent>
      </Card>
    </div>
  );
}
