import { createFileRoute, useNavigate } from "@tanstack/react-router";
import { LegRow, dotClass } from "@/components/route-legs";
import { startGuidance } from "@/lib/api";
import { getDest, getLastRoutes, getOrigin, getPrefs, isUsablePlace, setGuidance } from "@/lib/trip-store";
import { routeTotalMinutes } from "@/lib/transit-data";
import { useState } from "react";

export const Route = createFileRoute("/results/$routeId")({
  head: () => ({
    meta: [{ title: "경로 상세 — 세로이동" }],
  }),
  component: RouteDetailPage,
});

function RouteDetailPage() {
  const { routeId } = Route.useParams();
  const navigate = useNavigate();
  const prefs = getPrefs();
  const origin = getOrigin();
  const dest = getDest();
  const route = getLastRoutes().find((r) => r.id === routeId);
  const [status, setStatus] = useState("");

  if (!route) {
    return (
      <div className="mx-auto max-w-[430px] px-4 pt-10">
        <p className="text-sm">경로를 찾을 수 없습니다.</p>
        <button type="button" className="mt-3 font-bold" onClick={() => navigate({ to: "/results" })}>
          결과로 돌아가기
        </button>
      </div>
    );
  }

  const transferWait = route.legs.filter((l) => l.kind === "transfer").reduce((s, l) => s + l.minutes, 0);

  return (
    <div className="min-h-screen bg-background font-sans text-foreground">
      <div className="mx-auto max-w-[430px] px-4 pb-10 pt-5">
        <header className="flex items-start gap-2">
          <button type="button" aria-label="뒤로" className="text-lg" onClick={() => navigate({ to: "/results" })}>
            ‹
          </button>
          <div>
            <h1 className="text-sm font-bold">경로 상세</h1>
            <p className="font-mono text-[10px] text-muted-foreground">RT_02_01</p>
          </div>
        </header>

        <div className="relative mt-4 overflow-hidden rounded-3xl bg-ink-soft p-4">
          <p className="font-mono text-[10px] text-paper/60">MAP · 구간 강조는 목록에서 선택</p>
          <div className="mt-4 flex items-center gap-2">
            <span className="size-3 rounded-full bg-paper" />
            {route.legs
              .filter((l) => l.kind !== "transfer")
              .map((l, i) => (
                <span
                  key={i}
                  className={`h-1 flex-1 rounded-full ${l.kind === "walk" ? "bg-paper/30" : dotClass[l.lineColor ?? "bus"]}`}
                />
              ))}
            <span className="size-3 rounded-full bg-lime" />
          </div>
          <div className="mt-2 flex justify-between font-mono text-[10px] text-paper/50">
            <span>{origin?.name}</span>
            <span>{dest?.name}</span>
          </div>
        </div>

        <section className="clay-card mt-4 rounded-3xl p-4 ring-1 ring-border">
          <div className="mb-3 flex justify-between border-b border-border pb-3 text-[11px]">
            <span className="text-muted-foreground">
              {origin?.name} → {dest?.name}
            </span>
            <span className="font-mono font-bold">총 {routeTotalMinutes(route, prefs.walk_speed)}분 · 환승대기 {transferWait}분</span>
          </div>
          {route.legs.map((leg, i) => (
            <LegRow key={i} leg={leg} speed={prefs.walk_speed} last={i === route.legs.length - 1} />
          ))}
        </section>

        {status && <p className="mt-3 text-center text-[12px] text-muted-foreground">{status}</p>}

        <button
          type="button"
          className="mt-5 w-full rounded-full bg-lime py-3.5 text-[15px] font-bold text-primary-foreground"
          onClick={() => {
            if (!isUsablePlace(origin)) {
              setStatus("위치 권한이 없어 길안내를 시작할 수 없습니다.");
              return;
            }
            const run = () => {
              void startGuidance(route.id, origin)
                .then(() => {
                  setGuidance({ routeId: route.id, startedAt: new Date().toISOString() });
                  void navigate({ to: "/guidance" });
                })
                .catch((err: Error) => setStatus(err.message || "길안내를 시작하지 못했습니다."));
            };
            if (
              typeof Notification !== "undefined" &&
              (getPrefs().alert_alight || getPrefs().alert_transfer)
            ) {
              void Notification.requestPermission().finally(run);
            } else {
              run();
            }
          }}
        >
          길안내 시작
        </button>
      </div>
    </div>
  );
}
