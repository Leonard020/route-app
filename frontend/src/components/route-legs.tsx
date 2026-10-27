import { useEffect, useState } from "react";
import {
  formatCountdown,
  walkMinutes,
  type Leg,
  type Speed,
  SPEEDS,
} from "@/lib/transit-data";

export const lineChipClass: Record<string, string> = {
  line2: "bg-line2/10 text-line2",
  line4: "bg-line4/10 text-line4",
  line9: "bg-line9/10 text-line9",
  bus: "bg-bus/10 text-bus",
};

export const dotClass: Record<string, string> = {
  line2: "bg-line2",
  line4: "bg-line4",
  line9: "bg-line9",
  bus: "bg-bus",
};

export function LiveArrival({ seconds, stopsAway }: { seconds: number; stopsAway: number }) {
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

export function LegRow({ leg, speed, last }: { leg: Leg; speed: Speed; last: boolean }) {
  const mins = leg.kind === "walk" ? walkMinutes(leg.minutes, speed) : leg.minutes;
  const dot = leg.kind === "walk" || leg.kind === "transfer" ? "bg-ink" : dotClass[leg.lineColor ?? "bus"];

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
            <span className={`rounded-full px-2 py-0.5 text-[10px] font-semibold ${lineChipClass[leg.lineColor ?? "bus"]}`}>
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
