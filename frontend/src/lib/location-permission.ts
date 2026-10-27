import type { Place } from "@/lib/transit-data";

export const LOCATION_DECISION_KEY = "seoro.locationDecision";
export const ORIGIN_PLACE_KEY = "seoro.originPlace";
export const LOCATION_NOTICE_KEY = "seoro.locationNotice";

export type LocationDecision = "granted" | "denied";
export type LocationNotice = "denied" | "failed" | "accuracy" | null;

export function getLocationDecision(): LocationDecision | null {
  if (typeof window === "undefined") return null;
  const value = window.localStorage.getItem(LOCATION_DECISION_KEY);
  if (value === "granted" || value === "denied") return value;
  return null;
}

export function setLocationDecision(decision: LocationDecision): void {
  window.localStorage.setItem(LOCATION_DECISION_KEY, decision);
}

export function getSavedOrigin(): Place | null {
  if (typeof window === "undefined") return null;
  const raw = window.sessionStorage.getItem(ORIGIN_PLACE_KEY);
  if (!raw) return null;
  try {
    const parsed = JSON.parse(raw) as Place;
    if (parsed && typeof parsed.name === "string" && Number.isFinite(parsed.lat) && Number.isFinite(parsed.lng)) {
      return parsed;
    }
  } catch {
    return null;
  }
  return null;
}

export function saveOrigin(place: Place): void {
  window.sessionStorage.setItem(ORIGIN_PLACE_KEY, JSON.stringify(place));
}

export function getLocationNotice(): LocationNotice {
  if (typeof window === "undefined") return null;
  const value = window.sessionStorage.getItem(LOCATION_NOTICE_KEY);
  if (value === "denied" || value === "failed" || value === "accuracy") return value;
  return null;
}

export function setLocationNotice(notice: LocationNotice): void {
  if (!notice) {
    window.sessionStorage.removeItem(LOCATION_NOTICE_KEY);
    return;
  }
  window.sessionStorage.setItem(LOCATION_NOTICE_KEY, notice);
}

export function isUsablePlace(place: Place | null | undefined): place is Place {
  return Boolean(place && place.name && Number.isFinite(place.lat) && Number.isFinite(place.lng) && !place.placeholder);
}
