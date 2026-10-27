import { createFileRoute } from "@tanstack/react-router";
import { useState } from "react";
import { PhoneShell } from "@/components/tab-bar";
import { DEFAULT_PREFS, getPrefs, savePrefs, type RouteSort, type TravelPrefs } from "@/lib/trip-store";
import { SPEEDS, type Speed } from "@/lib/transit-data";

export const Route = createFileRoute("/settings")({
  head: () => ({
    meta: [{ title: "이동 설정 — 세로이동" }],
  }),
  component: SettingsPage,
});

const SORTS: { id: RouteSort; label: string }[] = [
  { id: "fastest", label: "빠른 도착" },
  { id: "min_transfer", label: "최소 환승" },
  { id: "min_walk", label: "최소 도보" },
];

function SettingsPage() {
  const [prefs, setPrefs] = useState<TravelPrefs>(() => (typeof window === "undefined" ? DEFAULT_PREFS : getPrefs()));
  const [custom, setCustom] = useState(prefs.custom_kmh !== null);
  const [saved, setSaved] = useState(true);
  const kmh = custom && prefs.custom_kmh ? prefs.custom_kmh : SPEEDS[prefs.walk_speed].kmh;
  const meters500min = Math.max(1, Math.round((0.5 / kmh) * 60));

  const commit = (next: TravelPrefs) => {
    setPrefs(next);
    savePrefs(next);
    setSaved(true);
  };

  return (
    <PhoneShell>
      <header>
        <h1 className="text-lg font-bold">이동 설정</h1>
        <p className="font-mono text-[10px] text-muted-foreground">ST_01_01</p>
      </header>

      <section className="clay-card mt-5 rounded-[28px] p-4 ring-1 ring-border">
        <h2 className="text-sm font-bold">걷기 속도</h2>
        <p className="mt-1 text-[12px] text-muted-foreground">도보 구간 시간 계산에 쓰여요.</p>
        <div className="mt-3 grid grid-cols-4 gap-1.5">
          {(Object.keys(SPEEDS) as Speed[]).map((s) => (
            <button
              key={s}
              type="button"
              onClick={() => {
                setCustom(false);
                commit({ ...prefs, walk_speed: s, custom_kmh: null });
              }}
              className={`rounded-xl py-2 text-[11px] font-semibold ${
                !custom && prefs.walk_speed === s ? "bg-ink text-paper" : "bg-muted"
              }`}
            >
              {SPEEDS[s].label}
            </button>
          ))}
          <button
            type="button"
            onClick={() => setCustom(true)}
            className={`rounded-xl py-2 text-[11px] font-semibold ${custom ? "bg-ink text-paper" : "bg-muted"}`}
          >
            직접 입력
          </button>
        </div>
        {custom && (
          <input
            type="number"
            min={2}
            max={8}
            step={0.1}
            value={prefs.custom_kmh ?? 4.8}
            onChange={(e) => {
              const v = Number(e.target.value);
              if (!Number.isFinite(v) || v < 2 || v > 8) return;
              const nearest: Speed = v <= 4 ? "slow" : v >= 5.5 ? "fast" : "normal";
              commit({ ...prefs, custom_kmh: v, walk_speed: nearest });
            }}
            className="mt-3 w-full rounded-xl bg-muted px-3 py-2 text-sm"
          />
        )}
        <p className="mt-3 font-mono text-sm font-bold">{kmh} km/h</p>
        <p className="text-[12px] text-muted-foreground">500m ≈ {meters500min}분</p>
      </section>

      <section className="clay-card mt-3 rounded-[28px] p-4 ring-1 ring-border">
        <h2 className="text-sm font-bold">경로 선호</h2>
        <div className="mt-3 grid grid-cols-3 gap-1.5">
          {SORTS.map((s) => (
            <button
              key={s.id}
              type="button"
              onClick={() => commit({ ...prefs, route_sort: s.id })}
              className={`rounded-xl py-2 text-[11px] font-semibold ${
                prefs.route_sort === s.id ? "bg-ink text-paper" : "bg-muted"
              }`}
            >
              {s.label}
            </button>
          ))}
        </div>
      </section>

      <section className="clay-card mt-3 rounded-[28px] p-4 ring-1 ring-border">
        <h2 className="text-sm font-bold">길안내 알림</h2>
        <label className="mt-3 flex items-center justify-between text-sm">
          하차 알림
          <input
            type="checkbox"
            checked={prefs.alert_alight}
            onChange={(e) => commit({ ...prefs, alert_alight: e.target.checked })}
          />
        </label>
        <label className="mt-3 flex items-center justify-between text-sm">
          환승 알림
          <input
            type="checkbox"
            checked={prefs.alert_transfer}
            onChange={(e) => commit({ ...prefs, alert_transfer: e.target.checked })}
          />
        </label>
        <p className="mt-4 text-[12px] text-muted-foreground">알림 시점</p>
        <input
          type="range"
          min={1}
          max={10}
          value={prefs.alert_minutes_before}
          onChange={(e) => commit({ ...prefs, alert_minutes_before: Number(e.target.value) })}
          className="mt-2 w-full"
        />
        <p className="font-mono text-sm font-bold">{prefs.alert_minutes_before}분 전</p>
        <p className="mt-2 text-[11px] text-muted-foreground">알림 권한이 없으면 길안내 화면 안에서만 알려드려요.</p>
      </section>

      {saved && <p className="mt-3 text-center text-[12px] text-muted-foreground">저장됨</p>}
    </PhoneShell>
  );
}
