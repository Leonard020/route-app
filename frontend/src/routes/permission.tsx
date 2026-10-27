import { createFileRoute, useNavigate } from "@tanstack/react-router";
import { useState } from "react";
import { resolveCurrentPlace } from "@/lib/api";
import {
  saveOrigin,
  setLocationDecision,
  setLocationNotice,
} from "@/lib/location-permission";

export const Route = createFileRoute("/permission")({
  head: () => ({
    meta: [
      { title: "위치 권한 안내 — 세로이동" },
      {
        name: "description",
        content: "현재 위치를 출발지로 쓰기 위해 위치정보 접근 권한을 안내합니다.",
      },
    ],
  }),
  component: PermissionPage,
});

const PURPOSES = [
  { icon: "📍", label: "현재 위치를 출발지로 자동 입력" },
  { icon: "🚏", label: "가까운 역·정류장 실시간 도착정보" },
  { icon: "🧭", label: "길안내 중 진행 단계·경로 이탈 감지" },
];

function PermissionPage() {
  const navigate = useNavigate();
  const [busy, setBusy] = useState(false);
  const [error, setError] = useState("");

  const goHome = () => {
    void navigate({ to: "/" });
  };

  const allow = () => {
    setBusy(true);
    setError("");
    void resolveCurrentPlace()
      .then((place) => {
        setLocationDecision("granted");
        saveOrigin(place);
        setLocationNotice(null);
        goHome();
      })
      .catch((err: Error) => {
        const denied = /거부|permission|denied/i.test(err.message);
        setLocationDecision("denied");
        setLocationNotice(denied ? "denied" : "failed");
        setError(
          denied
            ? "위치 권한이 없어 현재 위치를 확인할 수 없습니다. 직접 출발지를 입력하거나, 브라우저 설정에서 권한을 허용한 뒤 다시 시도하세요."
            : err.message || "현재 위치를 확인할 수 없습니다.",
        );
        setBusy(false);
      });
  };

  const skip = () => {
    setLocationDecision("denied");
    setLocationNotice("denied");
    goHome();
  };

  return (
    <div className="min-h-screen bg-background font-sans text-foreground antialiased">
      <div className="mx-auto flex min-h-screen max-w-[430px] flex-col px-4 pb-10 pt-5">
        <header className="flex items-center justify-center">
          <div className="text-center leading-tight">
            <p className="text-sm font-bold">위치 권한 안내</p>
            <p className="font-mono text-[10px] text-muted-foreground">CM_01_01</p>
          </div>
        </header>

        <div className="flex flex-1 flex-col items-center justify-center">
          <div className="mb-5 grid size-16 place-items-center rounded-full bg-lime/35">
            <span className="grid size-8 place-items-center rounded-full bg-lime text-lg font-bold text-primary-foreground">
              ◎
            </span>
          </div>

          <section className="clay-card w-full rounded-[28px] p-5 ring-1 ring-border animate-rise">
            <h1 className="text-lg font-bold tracking-tight">현재 위치를 출발지로 쓸까요?</h1>
            <p className="mt-1.5 text-[12px] text-muted-foreground">
              위치 정보는 다음 목적으로만 사용됩니다.
            </p>

            <ul className="mt-4 space-y-2">
              {PURPOSES.map((item) => (
                <li
                  key={item.label}
                  className="flex items-center gap-2 rounded-2xl bg-muted px-3 py-2.5 text-[13px] font-medium"
                >
                  <span aria-hidden="true">{item.icon}</span>
                  <span>{item.label}</span>
                </li>
              ))}
            </ul>

            <p className="mt-4 text-[11px] leading-relaxed text-muted-foreground">
              길안내 시작 시 하차·환승 알림을 위한 알림 권한도 요청합니다.
            </p>

            {error && (
              <p className="mt-3 rounded-2xl bg-muted px-3 py-2.5 text-[12px] text-foreground">{error}</p>
            )}

            <button
              type="button"
              disabled={busy}
              onClick={allow}
              className="mt-5 w-full rounded-full bg-lime py-3 text-[15px] font-bold text-primary-foreground disabled:opacity-70"
            >
              {busy ? "현재 위치 조회 중…" : error ? "다시 시도" : "위치 권한 허용"}
            </button>
            <button
              type="button"
              disabled={busy}
              onClick={skip}
              className="mt-2 w-full rounded-full bg-muted py-3 text-[15px] font-bold text-foreground disabled:opacity-70"
            >
              허용 안 함 · 직접 입력
            </button>
          </section>
        </div>
      </div>
    </div>
  );
}
