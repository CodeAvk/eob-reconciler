"use client";

import { FilePlus2, FolderOpen, ShieldCheck } from "lucide-react";
import Link from "next/link";
import { usePathname } from "next/navigation";

const NAV = [
  { href: "/", label: "Cases", icon: FolderOpen },
  { href: "/cases/new", label: "New case", icon: FilePlus2 },
];

export default function Shell({ children }: { children: React.ReactNode }) {
  const path = usePathname();
  return (
    <div className="shell">
      <aside className="sidebar">
        <Link href="/" className="brand">
          <ShieldCheck size={22} aria-hidden />
          <span>Bill Reconciler</span>
        </Link>
        <nav className="nav" aria-label="Primary">
          {NAV.map(({ href, label, icon: Icon }) => {
            const active = href === "/" ? path === "/" : path.startsWith(href);
            return (
              <Link key={href} href={href} className={active ? "nav-link active" : "nav-link"}
                aria-current={active ? "page" : undefined}>
                <Icon size={18} aria-hidden />
                <span>{label}</span>
              </Link>
            );
          })}
        </nav>
        <p className="sidebar-note">
          Findings are for review only and are not medical, legal or billing advice.
        </p>
      </aside>
      <main className="content">{children}</main>
    </div>
  );
}
