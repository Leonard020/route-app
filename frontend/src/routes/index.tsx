import { Link, createFileRoute, useNavigate } from "@tanstack/react-router";
import { useEffect, useState } from "react";
import { PhoneShell } from "@/components/tab-bar";
import { ErrorSheet, type ErrorKind } from "@/components/error-sheet";
import { resolveCurrentPlace } from "@/lib/api";
import { getLocationDecision, setLocationDecision, setLocationNotice } from "@/lib/location-permission";
import {
  FAVORITES,
  getDest,
  getOrigin,
  getPrefs,
  isUsablePlace,
  samePlace,
  setDest,
  setOrigin,
} from "@/lib/trip-store";
import { SPEEDS, type Place } from "@/lib/transit-data";

export const Route = createFileRoute("/")({
  head: () => ({
    meta: [
      { title: "세로이동 — 출발지·목적지 입력" },
      { name: "description", content: "출발지와 도착지를 입력하고 실시간 대중교통 경로를 탐색하세요." },
    ],
  }),
  component: HomePage,
});

function HomePage() {
  const navigate = useNavigate();
  const [ready, setReady] = useState(false);
  const [origin, setOriginState] = useState<Place | null>(null);
  const [dest, setDestState] = useState<Place | null>(null);
  const [locating, setLocating] = useState(false);
  const [error, setError] = useState<ErrorKind>(null);
  const prefs = typeof window === "undefined" ? null : getPrefs();

  useEffect(() => {
    if (!getLocationDecision()) {
      void navigate({ to: "/permission" });
      return;
    }
    setOriginState(getOrigin());
    setDestState(getDest());
    setReady(true);
  }, [navigate]);

  if (!ready) return null;

  const canSearch = isUsablePlace(origin) && isUsablePlace(dest);
  const sortLabel =
    prefs?.route_sort === "min_transfer" ? "최소 환승" : prefs?.route_sort === "min_walk" ? "최소 도보" : "빠른 도착";
  const speed = prefs?.walk_speed ?? "normal";

  const applyOrigin = (place: Place) => {
    setOrigin(place);
    setOriginState(place);
  };
  const applyDest = (place: Place) => {
    setDest(place);
    setDestState(place);
  };

  return (
    <PhoneShell>
      <header>
        <h1 className="text-sm font-bold">세로이동</h1>
        <p className="font-mono text-[10px] text-muted-foreground">HM_01_01</p>
      </header>

      <p className="mt-8 font-display text-4xl leading-tight">어디로 갈까요?</p>

      <section className="clay-card relative mt-5 rounded-[28px] p-4 ring-1 ring-border">
        <div className="flex items-stretch gap-3">
          <div className="min-w-0 flex-1">
            <Link
              to="/search"
              search={{ target: "origin" }}
              className="flex items-center gap-3 py-2"
            >
              <span className="grid size-8 shrink-0 place-items-center rounded-full bg-lime text-[10px] font-bold text-primary-foreground">
                출발
              </span>
              <span className="min-w-0">
                <span className="block truncate text-sm font-bold">{origin?.name || "출발지를 검색하세요"}</span>
                {origin?.detail && <span className="block truncate text-[11px] text-muted-foreground">{origin.detail}</span>}
              </span>
            </Link>
            {origin && (
              <button
                type="button"
                aria-label="출발지 지우기"
                className="absolute right-14 top-5 text-muted-foreground"
                onClick={() => {
                  setOrigin(null);
                  setOriginState(null);
                }}
              >
                ×
              </button>
            )}
            <div className="ml-4 border-t border-border" />
            <Link to="/search" search={{ target: "destination" }} className="flex items-center gap-3 py-2">
              <span className="grid size-8 shrink-0 place-items-center rounded-full bg-ink text-[10px] font-bold text-paper">
                도착
              </span>
              <span className="min-w-0">
                <span className="block truncate text-sm font-bold">{dest?.name || "도착지를 검색하세요"}</span>
                {dest?.detail && <span className="block truncate text-[11px] text-muted-foreground">{dest.detail}</span>}
              </span>
            </Link>
            {dest && (
              <button
                type="button"
                aria-label="도착지 지우기"
                className="absolute right-14 bottom-5 text-muted-foreground"
                onClick={() => {
                  setDest(null);
                  setDestState(null);
                }}
              >
                ×
              </button>
            )}
          </div>
          <button
            type="button"
            aria-label="출발·도착 바꾸기"
            className="mt-6 grid size-10 shrink-0 place-items-center self-center rounded-full bg-muted text-sm font-bold"
            onClick={() => {
              const nextO = dest;
              const nextD = origin;
              if (nextO && isUsablePlace(nextO)) applyOrigin(nextO);
              else {
                setOrigin(null);
                setOriginState(null);
              }
              if (nextD && isUsablePlace(nextD)) applyDest(nextD);
              else {
                setDest(null);
                setDestState(null);
              }
            }}
          >
            ↑↓
          </button>
        </div>
      </section>

      <div className="mt-3 flex flex-wrap gap-1.5">
        <button
          type="button"
          disabled={locating}
          onClick={() => {
            setLocating(true);
            void resolveCurrentPlace()
              .then((place) => {
                setLocationDecision("granted");
                setLocationNotice(null);
                applyOrigin(place);
              })
              .catch((err: Error) => {
                setError(/거부|denied/i.test(err.message) ? "denied" : "failed");
              })
              .finally(() => setLocating(false));
          }}
          className="rounded-full bg-card px-3 py-2 text-[12px] font-semibold ring-1 ring-border"
        >
          {locating ? "위치 확인 중…" : "◎ 현재 위치를 출발지로"}
        </button>
        {FAVORITES.map((f) => (
          <button
            key={f.short}
            type="button"
            onClick={() => applyDest(f.place)}
            className="rounded-full bg-card px-3 py-2 text-[12px] font-semibold ring-1 ring-border"
          >
            ★ {f.short}
          </button>
        ))}
      </div>

      <button
        type="button"
        disabled={!canSearch}
        onClick={() => {
          if (!origin || !dest) return;
          if (samePlace(origin, dest)) {
            setError("same-place");
            return;
          }
          void navigate({ to: "/results" });
        }}
        className="mt-5 w-full rounded-full bg-lime py-3.5 text-[15px] font-bold text-primary-foreground disabled:opacity-40"
      >
        ⌕ 경로 탐색
      </button>
      {!canSearch && (
        <p className="mt-2 text-center text-[12px] text-muted-foreground">출발지와 도착지를 모두 입력하면 탐색할 수 있어요</p>
      )}

      <Link to="/settings" className="clay-card mt-5 block rounded-[28px] p-4 ring-1 ring-border">
        <div className="flex items-center justify-between">
          <p className="text-sm font-bold">내 이동 설정</p>
          <span className="text-[12px] text-muted-foreground">변경 ›</span>
        </div>
        <div className="mt-3 grid grid-cols-3 gap-2">
          <div className="rounded-2xl bg-muted px-2 py-3 text-center">
            <p className="text-[11px] text-muted-foreground">걷기</p>
            <p className="mt-1 text-sm font-bold">{SPEEDS[speed].label}</p>
            <p className="text-[10px] text-muted-foreground">{SPEEDS[speed].kmh}km/h</p>
          </div>
          <div className="rounded-2xl bg-muted px-2 py-3 text-center">
            <p className="text-[11px] text-muted-foreground">선호</p>
            <p className="mt-1 text-sm font-bold">{sortLabel}</p>
          </div>
          <div className="rounded-2xl bg-muted px-2 py-3 text-center">
            <p className="text-[11px] text-muted-foreground">알림</p>
            <p className="mt-1 text-sm font-bold">{prefs?.alert_minutes_before ?? 2}분 전</p>
            <p className="text-[10px] text-muted-foreground">하차·환승</p>
          </div>
        </div>
      </Link>

      <ErrorSheet
        kind={error}
        onRetry={
          error === "denied" || error === "failed"
            ? () => {
                setError(null);
                setLocating(true);
                void resolveCurrentPlace()
                  .then((place) => {
                    setLocationDecision("granted");
                    applyOrigin(place);
                  })
                  .catch(() => setError("failed"))
                  .finally(() => setLocating(false));
              }
            : undefined
        }
        onSearch={
          error
            ? () => {
                setError(null);
                void navigate({ to: "/search", search: { target: "origin" } });
              }
            : undefined
        }
      />
    </PhoneShell>
  );
}
