import { Link, useRouterState } from "@tanstack/react-router";

const TABS = [
  { to: "/", label: "홈", icon: "⌂" },
  { to: "/guidance", label: "안내", icon: "ⓘ" },
  { to: "/settings", label: "설정", icon: "⚙" },
] as const;

export function TabBar() {
  const pathname = useRouterState({ select: (s) => s.location.pathname });

  return (
    <nav className="fixed bottom-4 left-1/2 z-30 w-[min(100%-2rem,398px)] -translate-x-1/2 rounded-full bg-card p-1.5 shadow-lg ring-1 ring-border">
      <ul className="grid grid-cols-3">
        {TABS.map((tab) => {
          const active = pathname === tab.to;
          return (
            <li key={tab.to}>
              <Link
                to={tab.to}
                className={`flex flex-col items-center rounded-full py-2.5 text-[11px] font-semibold ${
                  active ? "bg-ink text-paper" : "text-muted-foreground"
                }`}
              >
                <span className="text-base leading-none">{tab.icon}</span>
                <span className="mt-1">{tab.label}</span>
              </Link>
            </li>
          );
        })}
      </ul>
    </nav>
  );
}

export function PhoneShell({ children }: { children: React.ReactNode }) {
  return (
    <div className="min-h-screen bg-background font-sans text-foreground antialiased">
      <div className="mx-auto max-w-[430px] px-4 pb-28 pt-5">{children}</div>
      <TabBar />
    </div>
  );
}
