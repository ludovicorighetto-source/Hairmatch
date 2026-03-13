import type { Metadata } from "next";
import { LoginForm } from "@/components/auth/LoginForm";
import {
  Card,
  CardHeader,
  CardTitle,
  CardDescription,
  CardContent,
} from "@/components/ui/card";

export const metadata: Metadata = {
  title: "Accedi",
  description: "Accedi al tuo account HairMatch",
};

export default function LoginPage() {
  return (
    <div className="w-full max-w-md">
      <Card className="shadow-lg">
        <CardHeader className="text-center">
          <CardTitle className="text-2xl font-bold">Bentornato</CardTitle>
          <CardDescription>
            Inserisci le tue credenziali per accedere
          </CardDescription>
        </CardHeader>
        <CardContent>
          <LoginForm />
        </CardContent>
      </Card>
    </div>
  );
}
