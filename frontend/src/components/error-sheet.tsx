export type ErrorKind = "denied" | "failed" | "accuracy" | "network" | "no-route" | "same-place" | null;

const COPY: Record<Exclude<ErrorKind, null>, { code: string; title: string; body: string }> = {
  denied: {
    code: "ER_01_01 · loc-denied",
    title: "위치 권한이 필요해요",
    body: "브라우저 설정에서 위치 권한을 허용하거나, 출발지를 직접 검색하세요.",
  },
  failed: {
    code: "ER_01_01 · loc-fail",
    title: "현재 위치를 확인할 수 없습니다",
    body: "측위에 실패했습니다. 다시 시도하거나 출발지를 검색하세요.",
  },
  accuracy: {
    code: "ER_01_01 · loc-accuracy",
    title: "위치 정확도가 낮아요",
    body: "현재 위치 오차가 커서 출발 지점이 다를 수 있습니다. 정확한 출발지를 검색하는 것을 권장합니다.",
  },
  network: {
    code: "ER_01_01 · network",
    title: "네트워크 연결을 확인해주세요",
    body: "실시간 정보를 불러오지 못했습니다. 다시 시도하거나 이전 결과를 확인하세요.",
  },
  "no-route": {
    code: "ER_01_01 · no-route",
    title: "이동 가능한 경로를 찾지 못했습니다",
    body: "출발지·도착지를 바꾸거나 다시 탐색해 주세요. 운행이 끝났을 수도 있습니다.",
  },
  "same-place": {
    code: "ER_01_01 · same-place",
    title: "출발지와 다른 목적지를 선택해주세요",
    body: "같은 장소로는 경로를 탐색할 수 없습니다.",
  },
};

export function ErrorSheet({
  kind,
  onRetry,
  onSearch,
  onClose,
}: {
  kind: ErrorKind;
  onRetry?: () => void;
  onSearch?: () => void;
  onClose?: () => void;
}) {
  if (!kind) return null;
  const copy = COPY[kind];
  return (
    <div className="fixed inset-0 z-40 flex items-end justify-center bg-ink/40 p-4">
      <div className="w-full max-w-[398px] rounded-[28px] bg-card p-5 shadow-xl animate-rise">
        <p className="font-mono text-[10px] text-muted-foreground">{copy.code}</p>
        <h2 className="mt-1 text-base font-bold">{copy.title}</h2>
        <p className="mt-2 text-[13px] leading-relaxed text-muted-foreground">{copy.body}</p>
        <div className="mt-4 flex gap-2">
          {onRetry && (
            <button
              type="button"
              onClick={onRetry}
              className="flex-1 rounded-full bg-lime py-3 text-sm font-bold text-primary-foreground"
            >
              다시 시도
            </button>
          )}
          {onSearch && (
            <button
              type="button"
              onClick={onSearch}
              className="flex-1 rounded-full bg-muted py-3 text-sm font-bold"
            >
              장소 검색
            </button>
          )}
          {onClose && !onRetry && !onSearch && (
            <button
              type="button"
              onClick={onClose}
              className="flex-1 rounded-full bg-lime py-3 text-sm font-bold text-primary-foreground"
            >
              확인
            </button>
          )}
        </div>
      </div>
    </div>
  );
}
