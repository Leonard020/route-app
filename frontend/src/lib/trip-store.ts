import type { Place, RouteOption, Speed } from "@/lib/transit-data";
import { PLACES } from "@/lib/transit-data";
import { getSavedOrigin, saveOrigin } from "@/lib/location-permission";

const DEST_KEY = "seoro.destPlace";
const RECENTS_KEY = "seoro.recents";
const PREFS_KEY = "seoro.prefs";
const ROUTES_KEY = "seoro.lastRoutes";
const GUIDANCE_KEY = "seoro.guidance";

export type RouteSort = "fastest" | "min_transfer" | "min_walk";

export type TravelPrefs = {
  walk_speed: Speed;
  custom_kmh: number | null;
  route_sort: RouteSort;
  alert_alight: boolean;
  alert_transfer: boolean;
  alert_minutes_before: number;
};

export const DEFAULT_PREFS: TravelPrefs = {
  walk_speed: "normal",
  custom_kmh: null,
  route_sort: "fastest",
  alert_alight: true,
  alert_transfer: true,
  alert_minutes_before: 2,
};

export const FAVORITES: { short: string; place: Place }[] = [
  { short: "집", place: PLACES.find((p) => p.name.startsWith("집")) ?? PLACES[11]! },
  { short: "회사", place: PLACES.find((p) => p.name.startsWith("회사")) ?? PLACES[10]! },
  {
    short: "헬스장",
    place: { name: "헬스장 (역삼)", detail: "즐겨찾기", lat: 37.5001, lng: 127.0352 },
  },
];

function readJson<T>(storage: Storage, key: string): T | null {
  try {
    const raw = storage.getItem(key);
    return raw ? (JSON.parse(raw) as T) : null;
  } catch {
    return null;
  }
}

export function isUsablePlace(place: Place | null | undefined): place is Place {
  return Boolean(place && place.name && Number.isFinite(place.lat) && Number.isFinite(place.lng) && !place.placeholder);
}

export function getOrigin(): Place | null {
  return getSavedOrigin();
}

export function setOrigin(place: Place | null): void {
  if (!place) {
    window.sessionStorage.removeItem("seoro.originPlace");
    return;
  }
  saveOrigin(place);
  pushRecent(place);
}

export function getDest(): Place | null {
  if (typeof window === "undefined") return null;
  return readJson<Place>(window.sessionStorage, DEST_KEY);
}

export function setDest(place: Place | null): void {
  if (!place) {
    window.sessionStorage.removeItem(DEST_KEY);
    return;
  }
  window.sessionStorage.setItem(DEST_KEY, JSON.stringify(place));
  pushRecent(place);
}

export function getRecents(): Place[] {
  if (typeof window === "undefined") return [];
  return readJson<Place[]>(window.localStorage, RECENTS_KEY) ?? [];
}

export function pushRecent(place: Place): void {
  if (!isUsablePlace(place)) return;
  const next = [place, ...getRecents().filter((p) => p.name !== place.name || p.lat !== place.lat)].slice(0, 8);
  window.localStorage.setItem(RECENTS_KEY, JSON.stringify(next));
}

export function removeRecent(place: Place): void {
  const next = getRecents().filter((p) => !(p.name === place.name && p.lat === place.lat && p.lng === place.lng));
  window.localStorage.setItem(RECENTS_KEY, JSON.stringify(next));
}

export function getPrefs(): TravelPrefs {
  if (typeof window === "undefined") return DEFAULT_PREFS;
  return { ...DEFAULT_PREFS, ...(readJson<Partial<TravelPrefs>>(window.localStorage, PREFS_KEY) ?? {}) };
}

export function savePrefs(prefs: TravelPrefs): void {
  window.localStorage.setItem(PREFS_KEY, JSON.stringify(prefs));
}

export function getLastRoutes(): RouteOption[] {
  if (typeof window === "undefined") return [];
  return readJson<RouteOption[]>(window.sessionStorage, ROUTES_KEY) ?? [];
}

export function setLastRoutes(routes: RouteOption[]): void {
  window.sessionStorage.setItem(ROUTES_KEY, JSON.stringify(routes));
}

export type GuidanceState = {
  routeId: string;
  startedAt: string;
};

export function getGuidance(): GuidanceState | null {
  if (typeof window === "undefined") return null;
  return readJson<GuidanceState>(window.sessionStorage, GUIDANCE_KEY);
}

export function setGuidance(state: GuidanceState | null): void {
  if (!state) {
    window.sessionStorage.removeItem(GUIDANCE_KEY);
    return;
  }
  window.sessionStorage.setItem(GUIDANCE_KEY, JSON.stringify(state));
}

export function samePlace(a: Place, b: Place): boolean {
  return a.name === b.name && Math.abs(a.lat - b.lat) < 0.0001 && Math.abs(a.lng - b.lng) < 0.0001;
}
