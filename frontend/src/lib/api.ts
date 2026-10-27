import type { Leg, Place, RouteOption } from "@/lib/transit-data";

const API_BASE = String(import.meta.env.VITE_API_BASE ?? "").replace(/\/$/, "");

function apiUrl(path: string): string {
  const p = path.startsWith("/") ? path : `/${path}`;
  return `${API_BASE}${p}`;
}

export type ApiPlace = {
  id: string;
  name: string;
  address?: string;
  category?: string | null;
  lat: number;
  lng: number;
  station_id?: string;
  subway_id?: string;
};

export type SelectedPlace = {
  name: string;
  detail: string;
  lat: number;
  lng: number;
  place_id?: string;
};

type Envelope<T> = {
  success: boolean;
  data: T;
  error?: { code?: string; message?: string };
};

async function readEnvelope<T>(res: Response): Promise<T> {
  const json = (await res.json()) as Envelope<T>;
  if (!res.ok || json.success === false) {
    throw new Error(json.error?.message || "요청에 실패했습니다.");
  }
  return json.data;
}

export async function searchPlaces(q: string): Promise<ApiPlace[]> {
  const res = await fetch(apiUrl(`/api/v1/places/search?q=${encodeURIComponent(q)}`));
  const data = await readEnvelope<{ items: ApiPlace[] }>(res);
  return data.items ?? [];
}

export async function resolveCurrentPlace(): Promise<Place> {
  const pos = await new Promise<GeolocationPosition>((resolve, reject) => {
    if (!navigator.geolocation) {
      reject(new Error("이 브라우저에서는 위치를 사용할 수 없습니다."));
      return;
    }
    navigator.geolocation.getCurrentPosition(resolve, () => reject(new Error("위치 권한이 거부되었습니다.")), {
      enableHighAccuracy: true,
      timeout: 8000,
    });
  });
  const lat = pos.coords.latitude;
  const lng = pos.coords.longitude;
  const params = new URLSearchParams({
    lat: String(lat),
    lng: String(lng),
    accuracy_m: String(pos.coords.accuracy ?? ""),
    permission: "true",
  });
  const res = await fetch(apiUrl(`/api/v1/location/current?${params.toString()}`));
  const data = await readEnvelope<{
    lat: number;
    lng: number;
    name: string;
    address?: string | null;
    place_id?: string;
  }>(res);
  return {
    name: data.name || "현재 위치",
    detail: data.address || "현재 위치",
    lat: data.lat,
    lng: data.lng,
    place_id: data.place_id,
  };
}

function lineColor(subwayId?: string | null, mode?: string): Leg["lineColor"] {
  if (mode === "bus") return "bus";
  if (subwayId === "1002") return "line2";
  if (subwayId === "1004") return "line4";
  if (subwayId === "1009") return "line9";
  return mode === "subway" ? "line2" : "bus";
}

function toMinutes(seconds: number | undefined | null): number {
  return Math.max(1, Math.round((seconds ?? 60) / 60));
}

export function mapBackendRoute(route: Record<string, unknown>): RouteOption {
  const summary = (route.summary ?? {}) as Record<string, unknown>;
  const steps = (route.steps ?? []) as Record<string, unknown>[];
  const legs: Leg[] = [];
  let firstTransit = true;
  for (const step of steps) {
    const mode = String(step.mode ?? "");
    const info = (step.transit_info ?? {}) as Record<string, unknown>;
    const duration = Number(step.duration_s ?? 0);
    if (mode === "walk") {
      legs.push({
        kind: "walk",
        title: "도보",
        sub: String(step.instruction ?? "도보 이동"),
        minutes: toMinutes(duration),
      });
      continue;
    }
    if (mode === "bus" || mode === "subway") {
      const wait = Number(info.wait_seconds ?? 0);
      if (!firstTransit && wait > 0) {
        legs.push({
          kind: "transfer",
          title: "환승 대기",
          sub: String(info.warning ?? info.alight_stop ?? info.alight_station ?? "환승"),
          minutes: toMinutes(wait),
        });
      }
      firstTransit = false;
      const ride = Math.max(duration - wait, 60);
      const line = String(info.route_no ?? info.train_line_nm ?? info.line_name ?? (mode === "bus" ? "버스" : "지하철"));
      const arrival =
        typeof info.arr_time_seconds === "number"
          ? info.arr_time_seconds
          : typeof info.arrival_seconds === "number"
            ? info.arrival_seconds
            : wait > 0
              ? wait
              : null;
      const stops = typeof info.arr_prev_station_cnt === "number" ? info.arr_prev_station_cnt : null;
      const leg: Leg = {
        kind: mode,
        title: mode === "bus" ? `버스 ${line}` : `지하철 ${line}`,
        sub: String(step.instruction ?? ""),
        minutes: toMinutes(ride),
        line,
        lineColor: lineColor(info.subway_id as string | undefined, mode),
      };
      if (typeof arrival === "number") leg.arrivalSeconds = arrival;
      if (typeof stops === "number") leg.stopsAway = stops;
      legs.push(leg);
    }
  }
  return {
    id: String(route.route_id ?? "route"),
    fare: Number(summary.total_cost ?? 0),
    transfers: Number(summary.transfer_count ?? 0),
    fromApi: true,
    legs,
  };
}

export async function recommendRoutes(
  origin: SelectedPlace,
  destination: SelectedPlace,
  walkSpeed: "slow" | "normal" | "fast",
): Promise<RouteOption[]> {
  const res = await fetch(apiUrl("/api/v1/routes/recommend"), {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({
      origin: {
        lat: origin.lat,
        lng: origin.lng,
        place_id: origin.place_id,
        name: origin.name,
      },
      destination: {
        lat: destination.lat,
        lng: destination.lng,
        place_id: destination.place_id,
        name: destination.name,
      },
      mode: "transit",
      preferences: { walk_speed: walkSpeed, route_sort: "fastest" },
      options: { top_n: 3, include_steps: true },
    }),
  });
  const data = await readEnvelope<{ routes: Record<string, unknown>[] }>(res);
  return (data.routes ?? []).map(mapBackendRoute);
}

export async function startGuidance(routeId: string, origin: SelectedPlace): Promise<void> {
  const res = await fetch(apiUrl("/api/v1/guidance/start"), {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({
      route_id: routeId,
      location_permission: true,
      notify_permission: true,
      current_location: { lat: origin.lat, lng: origin.lng, name: origin.name },
    }),
  });
  await readEnvelope(res);
}
