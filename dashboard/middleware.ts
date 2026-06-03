import { NextRequest, NextResponse } from "next/server";

// Lightweight HTTP Basic Auth gate. Vercel's built-in Authentication doesn't
// cover production on the free Hobby plan, so we protect the whole app here:
// every page, API route and Server Action requires the password (any username),
// checked against DASHBOARD_SECRET. If DASHBOARD_SECRET is unset (e.g. a quick
// local run) the gate is disabled.
export const config = {
  matcher: ["/((?!_next/static|_next/image|favicon.ico).*)"],
};

export function middleware(req: NextRequest) {
  const secret = process.env.DASHBOARD_SECRET;
  if (!secret) return NextResponse.next();

  const header = req.headers.get("authorization") || "";
  if (header.startsWith("Basic ")) {
    try {
      const decoded = atob(header.slice(6));
      const password = decoded.slice(decoded.indexOf(":") + 1);
      if (password === secret) return NextResponse.next();
    } catch {
      /* fall through to 401 */
    }
  }
  return new NextResponse("Authentication required", {
    status: 401,
    headers: { "WWW-Authenticate": 'Basic realm="Content Empire OS"' },
  });
}
