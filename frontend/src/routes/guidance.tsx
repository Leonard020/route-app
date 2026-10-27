import { Link, createFileRoute, useNavigate } from "@tanstack/react-router";
import { useMemo, useState } from "react";
import { PhoneShell } from "@/components/tab-bar";
import { LegRow } from "@/components/route-legs";
import { getDest, getGuidance, getLastRoutes, getOrigin, getPrefs, setGuidance } from "@/lib/trip-store";
import { etaClock, routeTotalMinutes } from "@/lib/transit-data";

export const Route = createFileRoute("/guidance")({
  head: () => ({
    meta: [{ title: "길안내 — 세로이동" }],
  }),
  component: GuidancePage,
});

function GuidancePage() {
  const navigate = useNavigate();
  const session = getGuidance();
  const prefs = getPrefs();
  const origin = getOrigin();
  const dest = getDest();
  const route = useMemo(() => getLastRoutes().find((r) => r.id === session?.routeId), [session?.routeId]);
  const [confirmEnd, setConfirmEnd] = useState(false);

  if (!session || !route) {
    return (
      <PhoneShell>
        <h1 className="text-lg font-bold">길안내</h1>
        <p className="font-mono text-[10px] text-muted-foreground">NV_01_01</p>
        <div className="clay-card mt-8 rounded-[28px] p-6 text-center ring-1 ring-border">
          <p className="text-sm font-bold">진행 중인 길안내가 없어요</p>
          <p className="mt-2 text-[12px] text-muted-foreground">경로를 탐색한 뒤 상세에서 길안내를 시작하세요.</p>
          <Link to="/" className="mt-4 inline-block rounded-full bg-lime px-5 py-2 text-sm font-bold text-primary-foreground">
            홈으로
          </Link>
        </div>
      </PhoneShell>
    );
  }

  const remaining = routeTotalMinutes(route, prefs.walk_speed);
  const current = route.legs[0];

  return (
    <PhoneShell>
      <h1 className="text-lg font-bold">실시간 길안내</h1>
      <p className="font-mono text-[10px] text-muted-foreground">NV_01_01</p>
      <p className="mt-1 text-[12px] text-muted-foreground">
        {origin?.name} → {dest?.name}
      </p>

      <section className="clay-card mt-4 rounded-[28px] p-4 ring-1 ring-border">
        <p className="text-[11px] text-muted-foreground">현재 단계</p>
        <p className="mt-1 text-lg font-bold">{current?.title ?? "이동 중"}</p>
        <p className="text-[12px] text-muted-foreground">{current?.sub ?? "다음 안내를 확인하세요"}</p>
        <p className="mt-3 font-mono text-sm font-bold">남은 약 {remaining}분 · {etaClock(remaining)} 도착</p>
      </section>

      <section className="clay-card mt-3 rounded-[28px] p-4 ring-1 ring-border">
        {route.legs.map((leg, i) => (
          <LegRow key={i} leg={leg} speed={prefs.walk_speed} last={i === route.legs.length - 1} />
        ))}
      </section>

      <button
        type="button"
        className="mt-5 w-full rounded-full bg-muted py-3 text-sm font-bold"
        onClick={() => setConfirmEnd(true)}
      >
        안내 종료
      </button>

      {confirmEnd && (
        <div className="fixed inset-0 z-40 flex items-end justify-center bg-ink/40 p-4">
          <div className="w-full max-w-[398px] rounded-[28px] bg-card p-5">
            <p className="text-sm font-bold">길안내를 종료하시겠습니까?</p>
            <div className="mt-4 flex gap-2">
              <button type="button" className="flex-1 rounded-full bg-ink py-3 text-sm font-bold text-paper" onClick={() => {
                setGuidance(null);
                void navigate({ to: "/" });
              }}>
                종료
              </button>
              <button type="button" className="flex-1 rounded-full bg-muted py-3 text-sm font-bold" onClick={() => setConfirmEnd(false)}>
                취소
              </button>
            </div>
          </div>
        </div>
      )}
    </PhoneShell>
  );
}
