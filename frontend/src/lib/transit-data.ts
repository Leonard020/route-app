export type Place = {
  name: string;
  detail: string;
  lat: number;
  lng: number;
  place_id?: string;
  placeholder?: boolean;
};

export const PLACES: Place[] = [
  { name: "강남역", detail: "서울 강남구 · 2호선·신분당선", lat: 37.4979, lng: 127.0276 },
  { name: "성수역", detail: "서울 성동구 · 2호선", lat: 37.5446, lng: 127.0559 },
  { name: "홍대입구역", detail: "서울 마포구 · 2호선·경의중앙·공항철도", lat: 37.5572, lng: 126.9254 },
  { name: "서울역", detail: "서울 중구 · 1호선·4호선·공항철도", lat: 37.5547, lng: 126.9707 },
  { name: "잠실역", detail: "서울 송파구 · 2호선·8호선", lat: 37.5133, lng: 127.1001 },
  { name: "여의도역", detail: "서울 영등포구 · 5호선·9호선", lat: 37.5216, lng: 126.9242 },
  { name: "건대입구역", detail: "서울 광진구 · 2호선·7호선", lat: 37.5404, lng: 127.0692 },
  { name: "COEX 스타필드", detail: "서울 강남구 삼성동", lat: 37.5116, lng: 127.0594 },
  { name: "서울숲", detail: "서울 성동구 성수동", lat: 37.5444, lng: 127.0374 },
  { name: "경복궁", detail: "서울 종로구 사직로", lat: 37.5796, lng: 126.977 },
  { name: "회사 (역삼동)", detail: "즐겨찾기", lat: 37.5007, lng: 127.0366 },
  { name: "집 (망원동)", detail: "즐겨찾기", lat: 37.556, lng: 126.91 },
  { name: "시청역", detail: "서울 중구 · 1호선·2호선", lat: 37.5651, lng: 126.977 },
];

export type LegKind = "walk" | "subway" | "bus" | "transfer";

export type Leg = {
  kind: LegKind;
  title: string;
  sub: string;
  /** 분 — walk legs are base minutes at 보통 speed */
  minutes: number;
  line?: string;
  lineColor?: "line2" | "line4" | "line9" | "bus";
  /** 실시간 도착 남은 초 */
  arrivalSeconds?: number;
  stopsAway?: number;
};

export type RouteOption = {
  id: string;
  fare: number;
  transfers: number;
  fromApi?: boolean;
  /** 대중교통 탑승 + 환승대기 합계 (도보 제외) */
  legs: Leg[];
};

export const ROUTES: RouteOption[] = [
  {
    id: "r1",
    fare: 1250,
    transfers: 1,
    legs: [
      { kind: "walk", title: "도보", sub: "강남역 9번 출구까지", minutes: 6 },
      {
        kind: "subway",
        title: "지하철 2호선",
        sub: "강남역 → 건대입구역 · 7정거장",
        minutes: 14,
        line: "2호선",
        lineColor: "line2",
        arrivalSeconds: 192,
        stopsAway: 2,
      },
      { kind: "transfer", title: "환승 대기", sub: "건대입구역 7호선 환승", minutes: 3 },
      {
        kind: "bus",
        title: "버스 지선 2222",
        sub: "건대입구 → 성수역 · 4정류장",
        minutes: 8,
        line: "2222",
        lineColor: "bus",
        arrivalSeconds: 48,
        stopsAway: 1,
      },
      { kind: "walk", title: "도보", sub: "성수역 2번 출구 → 목적지", minutes: 4 },
    ],
  },
  {
    id: "r2",
    fare: 1250,
    transfers: 0,
    legs: [
      { kind: "walk", title: "도보", sub: "강남역 버스정류장까지", minutes: 9 },
      {
        kind: "bus",
        title: "버스 간선 401",
        sub: "강남역 → 성수역 · 12정류장",
        minutes: 26,
        line: "401",
        lineColor: "bus",
        arrivalSeconds: 340,
        stopsAway: 3,
      },
      { kind: "walk", title: "도보", sub: "성수역 → 목적지", minutes: 5 },
    ],
  },
  {
    id: "r3",
    fare: 1500,
    transfers: 2,
    legs: [
      { kind: "walk", title: "도보", sub: "강남역 5번 출구까지", minutes: 4 },
      {
        kind: "subway",
        title: "지하철 9호선",
        sub: "신논현 → 동작 · 5정거장",
        minutes: 11,
        line: "9호선",
        lineColor: "line9",
        arrivalSeconds: 75,
        stopsAway: 1,
      },
      { kind: "transfer", title: "환승 대기", sub: "동작역 4호선 환승", minutes: 4 },
      {
        kind: "subway",
        title: "지하철 4호선",
        sub: "동작 → 충무로 · 6정거장",
        minutes: 13,
        line: "4호선",
        lineColor: "line4",
        arrivalSeconds: 0,
        stopsAway: 0,
      },
      { kind: "transfer", title: "환승 대기", sub: "충무로역 2호선 방면", minutes: 3 },
      {
        kind: "subway",
        title: "지하철 2호선",
        sub: "을지로4가 → 성수역 · 6정거장",
        minutes: 12,
        line: "2호선",
        lineColor: "line2",
        arrivalSeconds: 255,
        stopsAway: 2,
      },
      { kind: "walk", title: "도보", sub: "성수역 3번 출구 → 목적지", minutes: 3 },
    ],
  },
];

export type Speed = "slow" | "normal" | "fast";

export const SPEEDS: Record<Speed, { label: string; kmh: number; factor: number }> = {
  slow: { label: "느림", kmh: 3.6, factor: 1.33 },
  normal: { label: "보통", kmh: 4.8, factor: 1 },
  fast: { label: "빠름", kmh: 6.0, factor: 0.8 },
};

export const walkMinutes = (base: number, speed: Speed) =>
  Math.max(1, Math.round(base * SPEEDS[speed].factor));

export const routeWalkMinutes = (r: RouteOption, speed: Speed) =>
  r.legs
    .filter((l) => l.kind === "walk")
    .reduce((s, l) => s + (r.fromApi ? l.minutes : walkMinutes(l.minutes, speed)), 0);

export const routeRideMinutes = (r: RouteOption) =>
  r.legs.filter((l) => l.kind !== "walk").reduce((s, l) => s + l.minutes, 0);

export const routeTotalMinutes = (r: RouteOption, speed: Speed) =>
  routeWalkMinutes(r, speed) + routeRideMinutes(r);

/** 전체 도보 이동 시간 (직선 거리 기준 모형) */
export const WALK_ONLY_BASE = 48;
export const CAR_MINUTES = 31;

export const formatCountdown = (sec: number) =>
  sec <= 30 ? "곧 도착" : `${Math.floor(sec / 60)}분 ${String(sec % 60).padStart(2, "0")}초`;

export const formatClock = (d: Date) =>
  d.toLocaleTimeString("ko-KR", { hour12: false, hour: "2-digit", minute: "2-digit", second: "2-digit" });

export const etaClock = (minutes: number, from = new Date()) => {
  const d = new Date(from.getTime() + minutes * 60000);
  return d.toLocaleTimeString("ko-KR", { hour12: false, hour: "2-digit", minute: "2-digit" });
};
