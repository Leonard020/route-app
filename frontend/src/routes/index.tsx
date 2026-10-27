import { createFileRoute } from "@tanstack/react-router";
import { useEffect, useMemo, useRef, useState } from "react";
import {
  CAR_MINUTES,
  PLACES,
  ROUTES,
  SPEEDS,
  WALK_ONLY_BASE,
  etaClock,
  formatClock,
  formatCountdown,
  routeRideMinutes,
  routeTotalMinutes,
  routeWalkMinutes,
  walkMinutes,
  type Leg,
  type Place,
  type RouteOption,
  type Speed,
} from "@/lib/transit-data";
import { recommendRoutes, searchPlaces, startGuidance, type SelectedPlace } from "@/lib/api";

export const Route = createFileRoute("/")({
  head: () => ({
    meta: [
      { title: "세로이동 — 실시간 대중교통 길찾기" },
      {
        name: "description",
        content:
          "출발지·목적지 검색, 대중교통 경로 탐색, 버스·지하철 실시간 도착정보, 환승 대기시간, 보행속도 반영 도보시간까지 한 화면에서 비교하고 가장 빠른 경로를 추천받으세요.",
      },
      { property: "og:title", content: "세로이동 — 실시간 대중교통 길찾기" },
      {
        property: "og:description",
        content: "도보·자가용·대중교통 예상 도착시간을 비교하고 최속 경로를 추천받는 길찾기.",
      },
    ],
  }),
  component: TransitPlanner,
});

const lineChipClass: Record<string, string> = {
  line2: "bg-line2/10 text-line2",
  line4: "bg-line4/10 text-line4",
  line9: "bg-line9/10 text-line9",
  bus: "bg-bus/10 text-bus",
};

const dotClass: Record<string, string> = {
  line2: "bg-line2",
  line4: "bg-line4",
  line9: "bg-line9",
  bus: "bg-bus",
};

function PlaceField({
  label,
  value,
  onChange,
  tone,
}: {
  label: string;
  value: string;
  onChange: (p: Place) => void;
  tone: "origin" | "destination";
}) {
  const [query, setQuery] = useState("");
  const [open, setOpen] = useState(false);
  const [remote, setRemote] = useState<Place[]>([]);
  const boxRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    const onDown = (e: MouseEvent) => {
      if (boxRef.current && !boxRef.current.contains(e.target as Node)) setOpen(false);
    };
    document.addEventListener("mousedown", onDown);
    return () => document.removeEventListener("mousedown", onDown);
  }, []);

  useEffect(() => {
    const q = query.trim();
    if (!open) return;
    if (!q) {
      setRemote([]);
      return;
    }
    const t = window.setTimeout(() => {
      void searchPlaces(q)
        .then((items) =>
          setRemote(
            items
              .filter((p) => Number.isFinite(p.lat) && Number.isFinite(p.lng))
              .map((p) => ({
                name: p.name,
                detail: p.address || p.category || "",
                lat: p.lat,
                lng: p.lng,
              })),
          ),
        )
        .catch(() => setRemote([]));
    }, 250);
    return () => window.clearTimeout(t);
  }, [query, open]);

  const results = useMemo(() => {
    const q = query.trim();
    const local = !q
      ? PLACES.slice(0, 6)
      : PLACES.filter((p) => p.name.includes(q) || p.detail.includes(q)).slice(0, 6);
    const merged = [...remote];
    for (const p of local) {
      if (!merged.some((m) => m.name === p.name)) merged.push(p);
    }
    return merged.slice(0, 8);
  }, [query, remote]);

  const dark = tone === "destination";

  return (
    <div ref={boxRef} className="relative">
      <div
        className={`flex items-center gap-2 rounded-2xl px-3 py-2.5 ${
          dark ? "bg-ink text-primary-foreground" : "bg-muted"
        }`}
      >
        <span
          className={`font-mono text-[11px] ${dark ? "text-paper/50" : "text-muted-foreground"}`}
        >
          {label}
        </span>
        <input
          value={open ? query : value}
          onFocus={() => {
            setQuery("");
            setOpen(true);
          }}
          onChange={(e) => setQuery(e.target.value)}
          placeholder={open ? "역·장소 검색" : value}
          aria-label={`${label} 검색`}
          className={`w-full bg-transparent text-sm font-semibold outline-none ${
            dark
              ? "text-paper placeholder:text-paper/40"
              : "text-foreground placeholder:text-muted-foreground"
          }`}
        />
      </div>

      {open && (
        <ul className="absolute left-0 right-0 top-full z-20 mt-2 overflow-hidden rounded-2xl bg-card ring-1 ring-border animate-rise">
          {results.length === 0 && (
            <li className="px-3 py-3 text-[12px] text-muted-foreground">검색 결과가 없습니다</li>
          )}
          {results.map((p) => (
            <li key={p.name}>
              <button
                type="button"
                onClick={() => {
                  onChange(p);
                  setOpen(false);
                }}
                className="flex w-full flex-col items-start gap-0.5 px-3 py-2.5 text-left hover:bg-muted"
              >
                <span className="text-sm font-semibold">{p.name}</span>
                <span className="text-[11px] text-muted-foreground">{p.detail}</span>
              </button>
            </li>
          ))}
        </ul>
      )}
    </div>
  );
}

function LiveArrival({ seconds, stopsAway }: { seconds: number; stopsAway: number }) {
  const [left, setLeft] = useState(seconds);
  useEffect(() => {
    setLeft(seconds);
    const id = setInterval(() => setLeft((s) => (s <= 1 ? seconds : s - 1)), 1000);
    return () => clearInterval(id);
  }, [seconds]);

  return (
    <div className="mt-1.5 flex items-center gap-2 rounded-xl bg-muted px-2.5 py-1.5">
      <span className="size-1.5 rounded-full bg-lime-deep animate-tick" />
      <span className="font-mono text-[11px] font-bold tabular-nums">{formatCountdown(left)}</span>
      <span className="text-[10px] text-muted-foreground">
        {stopsAway <= 0 ? "전역 출발" : `${stopsAway}번째 전 역`}
      </span>
    </div>
  );
}

function LegRow({ leg, speed, last }: { leg: Leg; speed: Speed; last: boolean }) {
  const mins = leg.kind === "walk" ? walkMinutes(leg.minutes, speed) : leg.minutes;
  const dot =
    leg.kind === "walk" || leg.kind === "transfer" ? "bg-ink" : dotClass[leg.lineColor ?? "bus"];

  return (
    <div className="flex gap-3">
      <div className="flex flex-col items-center">
        <span className={`mt-1.5 size-2.5 shrink-0 rounded-full ${dot}`} />
        {!last && <span className="w-px flex-1 bg-border" />}
      </div>
      <div className={`flex-1 ${last ? "" : "pb-3"}`}>
        <div className="flex items-center justify-between gap-2">
          <p className="text-sm font-semibold">
            {leg.title} <span className="font-mono text-[12px] tabular-nums">{mins}분</span>
          </p>
          {leg.line && (
            <span
              className={`rounded-full px-2 py-0.5 text-[10px] font-semibold ${
                lineChipClass[leg.lineColor ?? "bus"]
              }`}
            >
              {leg.line}
            </span>
          )}
        </div>
        <p className="text-[11px] text-muted-foreground">
          {leg.sub}
          {leg.kind === "walk" ? ` · ${SPEEDS[speed].label} 속도 반영` : ""}
        </p>
        {leg.arrivalSeconds !== undefined && (
          <LiveArrival seconds={leg.arrivalSeconds} stopsAway={leg.stopsAway ?? 0} />
        )}
      </div>
    </div>
  );
}

function toSelected(p: Place): SelectedPlace {
  return { name: p.name, detail: p.detail, lat: p.lat, lng: p.lng };
}

function TransitPlanner() {
  const [originPlace, setOriginPlace] = useState<Place>(PLACES[0]!);
  const [destinationPlace, setDestinationPlace] = useState<Place>(PLACES[1]!);
  const origin = originPlace.name;
  const destination = destinationPlace.name;
  const [speed, setSpeed] = useState<Speed>("normal");
  const [selected, setSelected] = useState("r1");
  const [now, setNow] = useState<Date | null>(null);
  const [apiRoutes, setApiRoutes] = useState<RouteOption[] | null>(null);
  const [status, setStatus] = useState("");
  const [searching, setSearching] = useState(false);

  useEffect(() => {
    setNow(new Date());
    const id = setInterval(() => setNow(new Date()), 1000);
    return () => clearInterval(id);
  }, []);

  useEffect(() => {
    let cancelled = false;
    setSearching(true);
    setStatus("경로를 찾는 중…");
    void recommendRoutes(toSelected(originPlace), toSelected(destinationPlace), speed)
      .then((routes) => {
        if (cancelled) return;
        setApiRoutes(routes);
        setSelected(routes[0]?.id ?? "");
        setStatus(routes.length ? "" : "이동 가능한 경로를 찾지 못했습니다.");
      })
      .catch((err: Error) => {
        if (cancelled) return;
        setApiRoutes(null);
        setStatus(err.message || "실시간 경로를 불러오지 못해 예시 경로를 표시합니다.");
      })
      .finally(() => {
        if (!cancelled) setSearching(false);
      });
    return () => {
      cancelled = true;
    };
  }, [originPlace, destinationPlace, speed]);

  const ranked = useMemo(
    () =>
      [...(apiRoutes && apiRoutes.length > 0 ? apiRoutes : ROUTES)].sort(
        (a, b) => routeTotalMinutes(a, speed) - routeTotalMinutes(b, speed),
      ),
    [speed, apiRoutes],
  );
  const fastest: RouteOption = ranked[0]!;
  const transitMin = routeTotalMinutes(fastest, speed);
  const walkOnly = walkMinutes(WALK_ONLY_BASE, speed);
  const detail = ranked.find((r) => r.id === selected) ?? fastest;
  const detailTransferWait = detail.legs
    .filter((l) => l.kind === "transfer")
    .reduce((s, l) => s + l.minutes, 0);

  const modes = [
    { key: "transit", label: "대중교통", minutes: transitMin, note: `환승 ${fastest.transfers}회` },
    { key: "car", label: "자가용", minutes: CAR_MINUTES, note: "차량 9.4km" },
    { key: "walk", label: "도보", minutes: walkOnly, note: `${SPEEDS[speed].label} 속도` },
  ];
  const bestMode = modes.reduce((a, b) => (b.minutes < a.minutes ? b : a));

  return (
    <div className="min-h-screen bg-background font-sans text-foreground antialiased">
      <div className="mx-auto max-w-[430px] px-4 pb-14 pt-5">
        <header className="flex items-center justify-between">
          <div className="flex items-center gap-2">
            <div className="grid size-9 place-items-center rounded-2xl bg-ink font-display text-lg text-lime">
              세
            </div>
            <div className="leading-tight">
              <p className="text-sm font-bold">세로이동</p>
              <p className="font-mono text-[10px] text-muted-foreground">SEOUL TRANSIT · 실시간</p>
            </div>
          </div>
          <div className="flex items-center gap-1.5 rounded-full bg-card px-3 py-1.5 ring-1 ring-border">
            <span className="size-1.5 rounded-full bg-lime-deep animate-tick" />
            <span className="font-mono text-[11px] text-muted-foreground tabular-nums">
              {now ? formatClock(now) : "--:--:--"}
            </span>
          </div>
        </header>

        {/* 출발지 / 목적지 검색 */}
        <section className="clay-card relative z-10 mt-4 rounded-3xl p-3 ring-1 ring-border animate-rise">
          <div className="flex items-center gap-3">
            <div className="flex flex-col items-center py-1">
              <span className="size-2.5 rounded-full bg-ink" />
              <span className="h-4 w-px bg-border" />
              <span className="size-2.5 rounded-full bg-line2" />
            </div>
            <div className="flex-1 space-y-2">
              <PlaceField label="출발" value={origin} onChange={setOriginPlace} tone="origin" />
              <PlaceField
                label="목적"
                value={destination}
                onChange={setDestinationPlace}
                tone="destination"
              />
            </div>
            <button
              type="button"
              onClick={() => {
                setOriginPlace(destinationPlace);
                setDestinationPlace(originPlace);
              }}
              aria-label="출발지와 목적지 바꾸기"
              className="grid size-11 place-items-center rounded-2xl bg-lime text-lg font-bold text-primary-foreground"
            >
              ⇅
            </button>
          </div>
          <div className="mt-3 flex flex-wrap gap-1.5">
            {["집 (망원동)", "회사 (역삼동)", "강남역", "성수역"].map((name) => (
              <button
                key={name}
                type="button"
                onClick={() => {
                  const found = PLACES.find((p) => p.name === name);
                  if (found) setDestinationPlace(found);
                }}
                className="rounded-full bg-muted px-2.5 py-1 text-[11px] font-medium"
              >
                {name}
              </button>
            ))}
          </div>
        </section>

        {/* 수단별 예상 도착시간 */}
        <section className="mt-4 animate-rise [animation-delay:80ms]">
          <div className="mb-2 flex items-center justify-between">
            <h2 className="text-xs font-bold tracking-tight">예상 도착시간</h2>
            <span className="font-mono text-[10px] text-muted-foreground">ETA</span>
          </div>
          <div className="grid grid-cols-3 gap-2">
            {modes.map((m) => (
              <div key={m.key} className="clay-card rounded-2xl p-3 ring-1 ring-border">
                <p className="text-[11px] font-medium text-muted-foreground">{m.label}</p>
                <p className="mt-1 font-mono text-lg font-bold tabular-nums">{m.minutes}분</p>
                <p
                  className={`font-mono text-[10px] ${
                    m.key === bestMode.key ? "text-lime-deep" : "text-muted-foreground"
                  }`}
                >
                  {m.key === bestMode.key ? "가장 빠름" : m.note}
                </p>
                <p className="font-mono text-[10px] text-muted-foreground">
                  {now ? `${etaClock(m.minutes, now)} 도착` : "— 도착"}
                </p>
              </div>
            ))}
          </div>
        </section>

        {/* 보행 속도 */}
        <section className="mt-4 animate-rise [animation-delay:140ms]">
          <div className="mb-2 flex items-center justify-between">
            <h2 className="text-xs font-bold tracking-tight">보행 속도</h2>
            <span className="font-mono text-[10px] text-muted-foreground">
              {SPEEDS[speed].kmh}km/h · 도보시간 반영
            </span>
          </div>
          <div className="clay-card grid grid-cols-3 gap-1.5 rounded-2xl p-1.5 ring-1 ring-border">
            {(Object.keys(SPEEDS) as Speed[]).map((s) => (
              <button
                key={s}
                type="button"
                onClick={() => setSpeed(s)}
                className={`rounded-xl py-2 text-xs font-semibold transition-colors ${
                  speed === s ? "bg-ink text-paper" : "text-muted-foreground"
                }`}
              >
                {SPEEDS[s].label}
              </button>
            ))}
          </div>
        </section>

        {/* 경로 옵션 */}
        <section className="mt-5 animate-rise [animation-delay:200ms]">
          <div className="mb-2 flex items-center justify-between">
            <h2 className="text-xs font-bold tracking-tight">경로 옵션</h2>
            <span className="font-mono text-[10px] text-muted-foreground">
              {searching ? "검색 중" : `${ranked.length}개`}
            </span>
          </div>

          <div className="space-y-3">
            {ranked.map((r, i) => {
              const total = routeTotalMinutes(r, speed);
              const isFastest = i === 0;
              const isSelected = detail.id === r.id;
              return (
                <button
                  key={r.id}
                  type="button"
                  onClick={() => setSelected(r.id)}
                  className={`clay-card relative block w-full rounded-3xl p-4 text-left ${
                    isFastest
                      ? "ring-2 ring-lime-deep animate-pulse-soft"
                      : isSelected
                        ? "ring-2 ring-ink"
                        : "ring-1 ring-border"
                  }`}
                >
                  {isFastest && (
                    <span className="absolute -top-2.5 left-4 rounded-full bg-lime px-2.5 py-0.5 text-[10px] font-bold text-primary-foreground">
                      최속 경로
                    </span>
                  )}
                  <div className="flex items-start justify-between">
                    <div>
                      <p
                        className={`font-mono font-bold tabular-nums ${
                          isFastest ? "text-2xl" : "text-xl"
                        }`}
                      >
                        {total}분
                      </p>
                      <p className="text-[11px] text-muted-foreground">
                        환승 {r.transfers}회 · 도보 {routeWalkMinutes(r, speed)}분 · 탑승{" "}
                        {routeRideMinutes(r)}분
                      </p>
                    </div>
                    <div className="text-right">
                      <p className="font-mono text-sm font-bold tabular-nums">
                        {r.fare.toLocaleString("ko-KR")}원
                      </p>
                      <p className="font-mono text-[10px] text-muted-foreground">
                        {now ? `${etaClock(total, now)} 도착` : "— 도착"}
                      </p>
                    </div>
                  </div>
                  <div className="mt-3 flex flex-wrap gap-1.5">
                    {r.legs
                      .filter((l) => l.line)
                      .map((l, idx) => (
                        <span
                          key={`${r.id}-${idx}`}
                          className={`rounded-full px-2 py-0.5 text-[10px] font-semibold ${
                            lineChipClass[l.lineColor ?? "bus"]
                          }`}
                        >
                          {l.kind === "bus" ? `버스 ${l.line}` : l.line}
                        </span>
                      ))}
                  </div>
                </button>
              );
            })}
          </div>
        </section>

        {/* 경로 상세 + 실시간 도착 + 환승 대기 */}
        <section className="mt-5 animate-rise [animation-delay:260ms]">
          <div className="mb-2 flex items-center justify-between">
            <h2 className="text-xs font-bold tracking-tight">경로 상세</h2>
            <span className="font-mono text-[10px] text-muted-foreground">
              환승 대기 합계 {detailTransferWait}분
            </span>
          </div>
          <div className="clay-card rounded-3xl p-4 ring-1 ring-border">
            <div className="mb-3 flex items-center justify-between border-b border-border pb-3">
              <p className="text-[11px] text-muted-foreground">
                {origin} → {destination}
              </p>
              <p className="font-mono text-[11px] font-bold tabular-nums">
                총 {routeTotalMinutes(detail, speed)}분
              </p>
            </div>
            {detail.legs.map((leg, i) => (
              <LegRow
                key={`${detail.id}-leg-${i}`}
                leg={leg}
                speed={speed}
                last={i === detail.legs.length - 1}
              />
            ))}
          </div>
        </section>

        {/* 개략도 */}
        <section className="mt-5 animate-rise [animation-delay:320ms]">
          <div className="relative overflow-hidden rounded-3xl bg-ink-soft p-4">
            <div
              className="absolute inset-0 opacity-20"
              style={{
                backgroundImage:
                  "linear-gradient(#ffffff22 1px, transparent 1px), linear-gradient(90deg, #ffffff22 1px, transparent 1px)",
                backgroundSize: "28px 28px",
              }}
            />
            <div className="relative">
              <div className="flex items-center justify-between">
                <span className="font-mono text-[10px] text-paper/60">SCHEMATIC</span>
                <span className="font-mono text-[10px] text-lime">
                  {origin} → {destination}
                </span>
              </div>
              <div className="mt-4 flex items-center gap-2">
                <span className="size-3 shrink-0 rounded-full bg-paper" />
                {detail.legs
                  .filter((l) => l.kind !== "transfer")
                  .map((l, i) => (
                    <span
                      key={`sch-${i}`}
                      className={`h-1 flex-1 rounded-full ${
                        l.kind === "walk" ? "bg-paper/30" : dotClass[l.lineColor ?? "bus"]
                      }`}
                    />
                  ))}
                <span className="size-3 shrink-0 rounded-full bg-lime" />
              </div>
              <div className="mt-2 flex items-center justify-between font-mono text-[10px] text-paper/50">
                <span>{origin}</span>
                <span>{destination}</span>
              </div>
            </div>
          </div>
        </section>

        {status && (
          <p className="mt-3 text-center text-[11px] text-muted-foreground">{status}</p>
        )}
        <button
          type="button"
          onClick={() => {
            void startGuidance(detail.id, toSelected(originPlace)).catch(() => {
              setStatus("길안내를 시작하지 못했습니다. 백엔드 연결을 확인하세요.");
            });
          }}
          className="mt-5 w-full rounded-2xl bg-lime py-3.5 text-[15px] font-bold text-primary-foreground animate-rise [animation-delay:380ms]"
        >
          이 경로로 출발
        </button>
      </div>
    </div>
  );
}
