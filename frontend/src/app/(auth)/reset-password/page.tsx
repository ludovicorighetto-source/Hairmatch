import type { Metadata } from "next";
import { ResetPasswordForm } from "@/components/auth/ResetPasswordForm";
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from "@/components/ui/card";

export const metadata: Metadata = {
  title: "Nuova Password — HairMatch",
  description: "Imposta una nuova password per il tuo account",
};

interface Props {
  searchParams: Promise<{ access_token?: string }>;
}

export default async function ResetPasswordPage({ searchParams }: Props) {
  const { access_token } = await searchParams;

  return (
    <div className="w-full max-w-md">
      <Card className="shadow-lg">
        <CardHeader className="text-center">
          <CardTitle className="text-2xl font-bold">Nuova password</CardTitle>
          <CardDescription>
            Scegli una nuova password sicura per il tuo account.
          </CardDescription>
        </CardHeader>
        <CardContent>
          <ResetPasswordForm accessToken={access_token ?? ""} />
        </CardContent>
      </Card>
    </div>
  );
}
