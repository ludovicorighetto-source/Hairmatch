import { NextRequest, NextResponse } from "next/server";

/**
 * Middleware for HairMatch
 *
 * Strategy:
 * - Dashboard routes (/dashboard/*) are protected.
 *   We detect authentication by the presence of a refresh_token cookie
 *   (set by the backend as HttpOnly). If absent, redirect to /login.
 *
 * - The root path (/) redirects authenticated users to their dashboard.
 *   Unauthenticated users see the landing page.
 *
 * Note: We cannot verify the JWT here because the access token lives in
 * memory only (Zustand store on the client). We use the HttpOnly cookie
 * as a proxy indicator of an active session. The actual token validation
 * happens on every API call via the backend.
 */

const REFRESH_TOKEN_COOKIE = "refresh_token";

const PROTECTED_PATHS = ["/dashboard"];
const AUTH_PATHS = ["/login", "/register"];

function isProtectedPath(pathname: string): boolean {
  return PROTECTED_PATHS.some((p) => pathname.startsWith(p));
}

function isAuthPath(pathname: string): boolean {
  return AUTH_PATHS.some((p) => pathname.startsWith(p));
}

export function middleware(request: NextRequest) {
  const { pathname } = request.nextUrl;
  const refreshToken = request.cookies.get(REFRESH_TOKEN_COOKIE);
  const isAuthenticated = Boolean(refreshToken?.value);

  // Protect /dashboard/* routes
  if (isProtectedPath(pathname)) {
    if (!isAuthenticated) {
      const loginUrl = new URL("/login", request.url);
      loginUrl.searchParams.set("redirect", pathname);
      return NextResponse.redirect(loginUrl);
    }
  }

  // Redirect authenticated users away from auth pages
  if (isAuthPath(pathname) && isAuthenticated) {
    // We can't determine the role here (access token is in-memory),
    // so we redirect to a neutral route that the client will handle
    return NextResponse.redirect(new URL("/dashboard/redirect", request.url));
  }

  return NextResponse.next();
}

export const config = {
  matcher: [
    /*
     * Match all paths except:
     * - _next/static (static files)
     * - _next/image (image optimization)
     * - favicon.ico
     * - Public assets
     */
    "/((?!_next/static|_next/image|favicon.ico|.*\\.(?:svg|png|jpg|jpeg|gif|webp)$).*)",
  ],
};
