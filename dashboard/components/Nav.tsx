import Link from "next/link";

const links = [
  { href: "/", label: "Overzicht" },
  { href: "/board", label: "Content-board" },
  { href: "/channels", label: "Kanalen" },
  { href: "/analytics", label: "Analytics" },
  { href: "/calendar", label: "Kalender" },
];

export default function Nav() {
  return (
    <header className="border-b border-edge bg-panel/60 backdrop-blur sticky top-0 z-10">
      <div className="max-w-6xl mx-auto px-4 h-14 flex items-center gap-6">
        <Link href="/" className="font-semibold text-accent">Content Empire OS</Link>
        <nav className="flex gap-4 text-sm">
          {links.map((l) => (
            <Link key={l.href} href={l.href} className="text-slate-300 hover:text-white">
              {l.label}
            </Link>
          ))}
        </nav>
      </div>
    </header>
  );
}
