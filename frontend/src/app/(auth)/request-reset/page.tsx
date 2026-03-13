import type { Metadata } from "next";
import { RequestResetForm } from "@/components/auth/RequestResetForm";
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from "@/components/ui/card";

export const metadata: Metadata = {
  title: "Reimposta Password — HairMatch",
  description: "Richiedi un link per reimpostare la tua password",
};

export default function RequestResetPage() {
  return (
    <div className="w-full max-w-md">
      <Card className="shadow-lg">
        <CardHeader className="text-center">
          <CardTitle className="text-2xl font-bold">Password dimenticata?</CardTitle>
          <CardDescription>
            Inserisci la tua email e ti invieremo un link per reimpostare la password.
          </CardDescription>
        </CardHeader>
        <CardContent>
          <RequestResetForm />
        </CardContent>
      </Card>
    </div>
  );
}
