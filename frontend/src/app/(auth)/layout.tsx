import Link from "next/link";
import { Scissors } from "lucide-react";

export default function AuthLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <div className="min-h-screen bg-gradient-to-br from-indigo-50 via-white to-violet-50">
      {/* Header */}
      <header className="border-b bg-white/80 backdrop-blur-sm">
        <div className="mx-auto flex max-w-6xl items-center px-4 py-4">
          <Link href="/" className="flex items-center gap-2">
            <Scissors className="h-6 w-6 text-indigo-600" />
            <span className="text-xl font-bold text-gray-900">HairMatch</span>
          </Link>
        </div>
      </header>

      {/* Content */}
      <main className="flex min-h-[calc(100vh-65px)] items-start justify-center px-4 py-8 sm:py-12">
        {children}
      </main>
    </div>
  );
}
