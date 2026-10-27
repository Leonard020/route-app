import { createFileRoute, useNavigate } from "@tanstack/react-router";
import { useEffect, useMemo, useState } from "react";
import { searchPlaces, resolveCurrentPlace } from "@/lib/api";
import { PLACES, type Place } from "@/lib/transit-data";
import {
  getRecents,
  isUsablePlace,
  pushRecent,
  removeRecent,
  setDest,
  setOrigin,
} from "@/lib/trip-store";
import { setLocationDecision, setLocationNotice } from "@/lib/location-permission";

type SearchTarget = "origin" | "destination";

export const Route = createFileRoute("/search")({
  validateSearch: (search: Record<string, unknown>): { target: SearchTarget } => ({
    target: search.target === "destination" ? "destination" : "origin",
  }),
  head: () => ({
    meta: [{ title: "장소 검색 — 세로이동" }],
  }),
  component: SearchPage,
});

function highlight(name: string, q: string) {
  if (!q) return name;
  const i = name.indexOf(q);
  if (i < 0) return name;
  return (
    <>
      {name.slice(0, i)}
      <mark className="bg-lime/70 text-inherit">{name.slice(i, i + q.length)}</mark>
      {name.slice(i + q.length)}
    </>
  );
}

function SearchPage() {
  const { target } = Route.useSearch();
  const navigate = useNavigate();
  const [query, setQuery] = useState("");
  const [remote, setRemote] = useState<Place[]>([]);
  const [recents, setRecents] = useState<Place[]>([]);
  const [error, setError] = useState("");
  const [locating, setLocating] = useState(false);

  useEffect(() => {
    setRecents(getRecents());
  }, []);

  useEffect(() => {
    const q = query.trim();
    if (!q) {
      setRemote([]);
      setError("");
      return;
    }
    const t = window.setTimeout(() => {
      void searchPlaces(q)
        .then((items) => {
          const mapped = items
            .filter((p) => Number.isFinite(p.lat) && Number.isFinite(p.lng))
            .map((p) => ({
              name: p.name,
              detail: p.address || p.category || "",
              lat: p.lat,
              lng: p.lng,
              place_id: p.id,
            }));
          setRemote(mapped);
          setError(mapped.length ? "" : "검색 결과가 없습니다. 다른 검색어로 입력해주세요.");
        })
        .catch(() => {
          setRemote([]);
          setError("검색 중 오류가 발생했습니다.");
        });
    }, 250);
    return () => window.clearTimeout(t);
  }, [query]);

  const results = useMemo(() => {
    const q = query.trim();
    if (!q) return [];
    const local = PLACES.filter((p) => p.name.includes(q) || p.detail.includes(q));
    const merged = [...remote];
    for (const p of local) {
      if (!merged.some((m) => m.name === p.name)) merged.push(p);
    }
    return merged.slice(0, 12);
  }, [query, remote]);

  const pick = (place: Place) => {
    if (!isUsablePlace(place)) {
      setError("위치를 확인할 수 없습니다.");
      return;
    }
    pushRecent(place);
    if (target === "origin") setOrigin(place);
    else setDest(place);
    void navigate({ to: "/" });
  };

  const title = target === "origin" ? "출발지 검색" : "도착지 검색";

  return (
    <div className="min-h-screen bg-background font-sans text-foreground">
      <div className="mx-auto max-w-[430px] px-4 pb-10 pt-5">
        <header className="flex items-start gap-2">
          <button type="button" aria-label="뒤로" className="mt-0.5 text-lg" onClick={() => navigate({ to: "/" })}>
            ‹
          </button>
          <div>
            <h1 className="text-sm font-bold">{title}</h1>
            <p className="font-mono text-[10px] text-muted-foreground">SC_01_01</p>
          </div>
        </header>

        <div className="relative mt-4">
          <input
            value={query}
            onChange={(e) => setQuery(e.target.value)}
            placeholder="역, 정류장, 장소 이름"
            aria-label={`${title}어`}
            className="w-full rounded-full bg-card py-3 pl-10 pr-10 text-sm font-semibold ring-1 ring-border outline-none"
            autoFocus
          />
          <span className="pointer-events-none absolute left-4 top-1/2 -translate-y-1/2 text-muted-foreground">⌕</span>
          {query && (
            <button
              type="button"
              aria-label="검색어 지우기"
              className="absolute right-3 top-1/2 -translate-y-1/2 text-muted-foreground"
              onClick={() => setQuery("")}
            >
              ×
            </button>
          )}
        </div>

        {target === "origin" && !query && (
          <button
            type="button"
            disabled={locating}
            onClick={() => {
              setLocating(true);
              void resolveCurrentPlace()
                .then((place) => {
                  setLocationDecision("granted");
                  setLocationNotice(null);
                  pick(place);
                })
                .catch(() => setError("현재 위치를 확인할 수 없습니다."))
                .finally(() => setLocating(false));
            }}
            className="clay-card mt-3 flex w-full items-center gap-3 rounded-[24px] p-3 text-left ring-1 ring-border"
          >
            <span className="grid size-10 place-items-center rounded-full bg-lime text-lg font-bold text-primary-foreground">
              ◎
            </span>
            <span>
              <span className="block text-sm font-bold">{locating ? "위치 확인 중…" : "현재 위치"}</span>
              <span className="text-[11px] text-muted-foreground">GPS로 출발지 설정</span>
            </span>
          </button>
        )}

        {query.trim() ? (
          <ul className="mt-4 divide-y divide-border">
            {results.map((p) => (
              <li key={`${p.name}-${p.lat}`}>
                <button type="button" onClick={() => pick(p)} className="flex w-full items-start gap-3 py-3 text-left">
                  <span className="mt-0.5 text-muted-foreground">⌖</span>
                  <span>
                    <span className="block text-sm font-bold">{highlight(p.name, query.trim())}</span>
                    <span className="text-[11px] text-muted-foreground">{p.detail}</span>
                  </span>
                </button>
              </li>
            ))}
          </ul>
        ) : (
          <section className="mt-6">
            <h2 className="text-sm font-bold">최근 검색</h2>
            {recents.length === 0 && (
              <p className="mt-3 text-[12px] text-muted-foreground">최근 검색 내역이 없습니다.</p>
            )}
            <ul className="mt-2 divide-y divide-border">
              {recents.map((p) => (
                <li key={`${p.name}-${p.lat}`} className="flex items-center gap-2">
                  <button type="button" onClick={() => pick(p)} className="flex flex-1 items-start gap-3 py-3 text-left">
                    <span className="mt-0.5 text-muted-foreground">⏱</span>
                    <span>
                      <span className="block text-sm font-bold">{p.name}</span>
                      <span className="text-[11px] text-muted-foreground">{p.detail}</span>
                    </span>
                  </button>
                  <button
                    type="button"
                    aria-label={`${p.name} 최근 검색 삭제`}
                    className="px-2 text-muted-foreground"
                    onClick={() => {
                      if (!window.confirm("이 검색 기록을 삭제할까요?")) return;
                      removeRecent(p);
                      setRecents(getRecents());
                    }}
                  >
                    ×
                  </button>
                </li>
              ))}
            </ul>
          </section>
        )}

        {error && <p className="mt-4 text-center text-[12px] text-muted-foreground">{error}</p>}
        {error.includes("오류") && (
          <button type="button" className="mx-auto mt-2 block text-[12px] font-bold" onClick={() => setQuery(query + " ")}>
            재시도
          </button>
        )}
      </div>
    </div>
  );
}
