import { Link, createFileRoute, useNavigate } from "@tanstack/react-router";
import { useEffect, useMemo, useState } from "react";
import { lineChipClass } from "@/components/route-legs";
import { ErrorSheet, type ErrorKind } from "@/components/error-sheet";
import { recommendRoutes } from "@/lib/api";
import {
  getDest,
  getOrigin,
  getPrefs,
  isUsablePlace,
  setLastRoutes,
} from "@/lib/trip-store";
import {
  ROUTES,
  etaClock,
  routeTotalMinutes,
  routeWalkMinutes,
  routeRideMinutes,
  type RouteOption,
} from "@/lib/transit-data";

export const Route = createFileRoute("/results")({
  head: () => ({
    meta: [{ title: "경로 탐색 결과 — 세로이동" }],
  }),
  component: ResultsPage,
});

function ResultsPage() {
  const navigate = useNavigate();
  const [routes, setRoutes] = useState<RouteOption[]>([]);
  const [searching, setSearching] = useState(true);
  const [fetchedAt, setFetchedAt] = useState<Date | null>(null);
  const [error, setError] = useState<ErrorKind>(null);
  const [status, setStatus] = useState("");
  const prefs = getPrefs();
  const origin = getOrigin();
  const dest = getDest();

  const load = () => {
    if (!isUsablePlace(origin) || !isUsablePlace(dest)) {
      void navigate({ to: "/" });
      return;
    }
    setSearching(true);
    setStatus("실시간 도착정보로 경로를 찾는 중…");
    void recommendRoutes(origin, dest, prefs.walk_speed, prefs.route_sort)
      .then((list) => {
        setRoutes(list);
        setLastRoutes(list);
        setFetchedAt(new Date());
        setError(list.length ? null : "no-route");
        setStatus("");
      })
      .catch(() => {
        setRoutes(ROUTES);
        setLastRoutes(ROUTES);
        setError("network");
        setStatus("정보를 갱신하지 못했습니다. 예시 경로를 표시합니다.");
      })
      .finally(() => setSearching(false));
  };

  useEffect(() => {
    load();
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, []);

  const ranked = useMemo(
    () => [...routes].sort((a, b) => routeTotalMinutes(a, prefs.walk_speed) - routeTotalMinutes(b, prefs.walk_speed)),
    [routes, prefs.walk_speed],
  );
  const sortLabel =
    prefs.route_sort === "min_transfer" ? "최소 환승 순" : prefs.route_sort === "min_walk" ? "최소 도보 순" : "빠른 도착 순";

  return (
    <div className="min-h-screen bg-background font-sans text-foreground">
      <div className="mx-auto max-w-[430px] px-4 pb-10 pt-5">
        <header className="flex items-start justify-between gap-2">
          <div className="flex items-start gap-2">
            <button type="button" aria-label="뒤로" className="text-lg" onClick={() => navigate({ to: "/" })}>
              ‹
            </button>
            <div>
              <h1 className="text-sm font-bold">경로 탐색 결과</h1>
              <p className="font-mono text-[10px] text-muted-foreground">RT_01_01</p>
              <p className="mt-1 text-[11px] text-muted-foreground">
                {origin?.name} → {dest?.name}
              </p>
            </div>
          </div>
          <button type="button" disabled={searching} className="text-[11px] font-bold text-lime-deep" onClick={load}>
            새로고침
          </button>
        </header>

        <p className="mt-4 text-[12px] font-semibold">{sortLabel}</p>
        {fetchedAt && (
          <p className="font-mono text-[10px] text-muted-foreground">마지막 조회 {fetchedAt.toLocaleTimeString("ko-KR")}</p>
        )}
        {status && <p className="mt-3 text-[12px] text-muted-foreground">{status}</p>}

        <div className="mt-4 space-y-3">
          {ranked.map((r, i) => {
            const total = routeTotalMinutes(r, prefs.walk_speed);
            const isFastest = i === 0;
            return (
              <Link
                key={r.id}
                to="/results/$routeId"
                params={{ routeId: r.id }}
                className={`clay-card relative block rounded-3xl p-4 ${
                  isFastest ? "ring-2 ring-lime-deep" : "ring-1 ring-border"
                }`}
              >
                {isFastest && (
                  <span className="absolute -top-2.5 left-4 rounded-full bg-lime px-2.5 py-0.5 text-[10px] font-bold text-primary-foreground">
                    최속 경로
                  </span>
                )}
                <div className="flex items-start justify-between">
                  <div>
                    <p className={`font-mono font-bold tabular-nums ${isFastest ? "text-2xl" : "text-xl"}`}>{total}분</p>
                    <p className="text-[11px] text-muted-foreground">
                      환승 {r.transfers}회 · 도보 {routeWalkMinutes(r, prefs.walk_speed)}분 · 탑승 {routeRideMinutes(r)}분
                    </p>
                    <p className="font-mono text-[10px] text-muted-foreground">
                      {r.fromApi ? "실시간" : "시간표 기준"} · {etaClock(total)} 도착
                    </p>
                  </div>
                  <p className="font-mono text-sm font-bold">{r.fare.toLocaleString("ko-KR")}원</p>
                </div>
                <div className="mt-3 flex flex-wrap gap-1.5">
                  {r.legs
                    .filter((l) => l.line)
                    .map((l, idx) => (
                      <span
                        key={`${r.id}-${idx}`}
                        className={`rounded-full px-2 py-0.5 text-[10px] font-semibold ${lineChipClass[l.lineColor ?? "bus"]}`}
                      >
                        {l.kind === "bus" ? `버스 ${l.line}` : l.line}
                      </span>
                    ))}
                </div>
              </Link>
            );
          })}
        </div>
      </div>
      <ErrorSheet
        kind={error === "network" || error === "no-route" ? error : null}
        onRetry={() => {
          setError(null);
          load();
        }}
        onSearch={() => navigate({ to: "/" })}
      />
    </div>
  );
}
