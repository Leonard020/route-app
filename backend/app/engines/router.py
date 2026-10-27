from typing import List, Dict, Any, Optional, Tuple
from app.engines.graph import GraphProvider
from app.core.settings import settings
from app.domain.geo import haversine_m, walk_seconds


def _raw(place) -> dict:
    data = dict(place.raw or {})
    data.setdefault("name", place.name)
    data.setdefault("place_id", str(place.id))
    data.setdefault("lat", place.lat)
    data.setdefault("lng", place.lng)
    data.setdefault("external_id", place.external_id)
    data.setdefault("standard_stop_id", getattr(place, "standard_bus_stop_id", None) or data.get("standard_stop_id"))
    data.setdefault("ars_id", getattr(place, "ars_id", None) or data.get("ars_id"))
    data.setdefault("card_stop_id", data.get("card_stop_id") or data.get("station_id"))
    return data


class Router:
    def __init__(self, graph: GraphProvider):
        self.graph = graph

    async def find_candidates(
        self,
        origin: Tuple[float, float],
        destination: Tuple[float, float],
        mode: str,
        top_k: int = 5,
        preferences: Optional[dict] = None,
    ) -> List[Dict[str, Any]]:
        o_lat, o_lng = origin
        d_lat, d_lng = destination
        prefs = preferences or {}
        speed = prefs.get("walk_speed") or "normal"
        city = settings.DEFAULT_BUS_CITY_CODE
        max_walk_m = int(prefs.get("max_walk_min") or 20) * 60 * 1.25

        bus_o = await self.graph.nearest_place(o_lat, o_lng, "bus")
        bus_d = await self.graph.nearest_place(d_lat, d_lng, "bus")
        sub_o = await self.graph.nearest_place(o_lat, o_lng, "subway")
        sub_d = await self.graph.nearest_place(d_lat, d_lng, "subway")

        candidates: list[dict] = []
        if mode in ("transit", "multi", "walk"):
            if bus_o and bus_d:
                cand = self._bus_candidate(o_lat, o_lng, d_lat, d_lng, bus_o, bus_d, speed, city)
                if cand["walk_distance_m"] <= max_walk_m * 2:
                    candidates.append(cand)
            if sub_o and sub_d:
                cand = self._subway_candidate(o_lat, o_lng, d_lat, d_lng, sub_o, sub_d, speed)
                if cand["walk_distance_m"] <= max_walk_m * 2:
                    candidates.append(cand)
            if bus_o and sub_d:
                mid_bus = bus_d or bus_o
                mid_sub = sub_o or sub_d
                candidates.append(
                    self._mixed_candidate(
                        o_lat, o_lng, d_lat, d_lng, bus_o, mid_bus, mid_sub, sub_d, speed, city
                    )
                )

        if not candidates and mode in ("transit", "multi", "walk"):
            return []
        return candidates[: max(top_k, 1)]

    def _bus_candidate(self, o_lat, o_lng, d_lat, d_lng, bus_o, bus_d, speed, city) -> dict:
        w1 = haversine_m(o_lat, o_lng, bus_o.lat, bus_o.lng)
        w2 = haversine_m(bus_d.lat, bus_d.lng, d_lat, d_lng)
        ride = max(haversine_m(bus_o.lat, bus_o.lng, bus_d.lat, bus_d.lng), 400)
        raw_o, raw_d = _raw(bus_o), _raw(bus_d)
        return {
            "candidate_id": "cand-bus-1",
            "total_distance_m": int(w1 + ride + w2),
            "total_cost": 1500,
            "transfer_count": 0,
            "walk_distance_m": int(w1 + w2),
            "carbon_g": 280,
            "polyline": None,
            "segments": [
                {"distance_m": int(w1), "road_type": "walk", "congestion": 1},
                {"distance_m": int(ride), "road_type": "bus", "congestion": 2},
                {"distance_m": int(w2), "road_type": "walk", "congestion": 1},
            ],
            "steps": [
                self._walk("출발지에서 버스 정류장까지 도보", o_lat, o_lng, bus_o.lat, bus_o.lng, w1, speed),
                {
                    "mode": "bus",
                    "instruction": f"{raw_o.get('name')}에서 버스 승차",
                    "distance_m": int(ride),
                    "duration_s": max(int(ride / 6.0), 60),
                    "start": {"lat": bus_o.lat, "lng": bus_o.lng},
                    "end": {"lat": bus_d.lat, "lng": bus_d.lng},
                    "transit_info": {
                        "city_code": str(raw_o.get("city_code") or city),
                        "node_id": raw_o.get("node_id") or raw_o.get("external_id"),
                        "standard_stop_id": raw_o.get("standard_stop_id") or raw_o.get("external_id"),
                        "ars_id": raw_o.get("ars_id"),
                        "route_id": raw_o.get("route_id"),
                        "route_no": raw_o.get("route_no"),
                        "board_stop": raw_o.get("name"),
                        "alight_stop": raw_d.get("name"),
                        "alight_stop_id": raw_d.get("standard_stop_id") or raw_d.get("external_id"),
                        "source": "tago",
                        "service": "getSttnAcctoArvlPrearngeInfoList",
                    },
                },
                self._walk("하차 정류장에서 목적지까지 도보", bus_d.lat, bus_d.lng, d_lat, d_lng, w2, speed),
            ],
        }

    def _subway_candidate(self, o_lat, o_lng, d_lat, d_lng, sub_o, sub_d, speed) -> dict:
        w1 = haversine_m(o_lat, o_lng, sub_o.lat, sub_o.lng)
        w2 = haversine_m(sub_d.lat, sub_d.lng, d_lat, d_lng)
        ride = max(haversine_m(sub_o.lat, sub_o.lng, sub_d.lat, sub_d.lng), 400)
        raw_o, raw_d = _raw(sub_o), _raw(sub_d)
        station_name = (raw_o.get("station_name") or raw_o.get("name") or "").replace("역", "")
        return {
            "candidate_id": "cand-subway-1",
            "total_distance_m": int(w1 + ride + w2),
            "total_cost": 1500,
            "transfer_count": 1 if raw_o.get("subway_id") != raw_d.get("subway_id") else 0,
            "walk_distance_m": int(w1 + w2),
            "carbon_g": 160,
            "polyline": None,
            "segments": [
                {"distance_m": int(w1), "road_type": "walk", "congestion": 1},
                {"distance_m": int(ride), "road_type": "subway", "congestion": 1},
                {"distance_m": int(w2), "road_type": "walk", "congestion": 1},
            ],
            "steps": [
                self._walk("출발지에서 지하철역까지 도보", o_lat, o_lng, sub_o.lat, sub_o.lng, w1, speed),
                {
                    "mode": "subway",
                    "instruction": f"{raw_o.get('name')}에서 지하철 승차",
                    "distance_m": int(ride),
                    "duration_s": max(int(ride / 9.0), 60),
                    "start": {"lat": sub_o.lat, "lng": sub_o.lng},
                    "end": {"lat": sub_d.lat, "lng": sub_d.lng},
                    "transit_info": {
                        "subway_id": raw_o.get("subway_id"),
                        "station_id": raw_o.get("station_id") or raw_o.get("external_id"),
                        "card_stop_id": raw_o.get("card_stop_id") or raw_o.get("station_id") or raw_o.get("external_id"),
                        "station_name": station_name or None,
                        "updn_line": raw_o.get("updn_line"),
                        "board_station": raw_o.get("name"),
                        "alight_station": raw_d.get("name"),
                        "source": "seoul_subway",
                        "service": "realtimeStationArrival/ALL",
                    },
                },
                self._walk("하차역에서 목적지까지 도보", sub_d.lat, sub_d.lng, d_lat, d_lng, w2, speed),
            ],
        }

    def _mixed_candidate(
        self, o_lat, o_lng, d_lat, d_lng, bus_o, bus_mid, sub_mid, sub_d, speed, city
    ) -> dict:
        w1 = haversine_m(o_lat, o_lng, bus_o.lat, bus_o.lng)
        ride1 = max(haversine_m(bus_o.lat, bus_o.lng, bus_mid.lat, bus_mid.lng), 300)
        tw = haversine_m(bus_mid.lat, bus_mid.lng, sub_mid.lat, sub_mid.lng)
        ride2 = max(haversine_m(sub_mid.lat, sub_mid.lng, sub_d.lat, sub_d.lng), 300)
        w2 = haversine_m(sub_d.lat, sub_d.lng, d_lat, d_lng)
        raw_bo, raw_bm = _raw(bus_o), _raw(bus_mid)
        raw_sm, raw_sd = _raw(sub_mid), _raw(sub_d)
        station_name = (raw_sm.get("station_name") or raw_sm.get("name") or "").replace("역", "")
        return {
            "candidate_id": "cand-mixed-1",
            "total_distance_m": int(w1 + ride1 + tw + ride2 + w2),
            "total_cost": 3000,
            "transfer_count": 1,
            "walk_distance_m": int(w1 + tw + w2),
            "carbon_g": 220,
            "polyline": None,
            "segments": [
                {"distance_m": int(w1), "road_type": "walk", "congestion": 1},
                {"distance_m": int(ride1), "road_type": "bus", "congestion": 2},
                {"distance_m": int(tw), "road_type": "walk", "congestion": 1},
                {"distance_m": int(ride2), "road_type": "subway", "congestion": 1},
                {"distance_m": int(w2), "road_type": "walk", "congestion": 1},
            ],
            "steps": [
                self._walk("출발지에서 버스 정류장까지 도보", o_lat, o_lng, bus_o.lat, bus_o.lng, w1, speed),
                {
                    "mode": "bus",
                    "instruction": "버스로 환승역 이동",
                    "distance_m": int(ride1),
                    "duration_s": max(int(ride1 / 6.0), 60),
                    "start": {"lat": bus_o.lat, "lng": bus_o.lng},
                    "end": {"lat": bus_mid.lat, "lng": bus_mid.lng},
                    "transit_info": {
                        "city_code": str(raw_bo.get("city_code") or city),
                        "node_id": raw_bo.get("node_id") or raw_bo.get("external_id"),
                        "standard_stop_id": raw_bo.get("standard_stop_id") or raw_bo.get("external_id"),
                        "board_stop": raw_bo.get("name"),
                        "alight_stop": raw_bm.get("name"),
                        "alight_stop_id": raw_bm.get("standard_stop_id") or raw_bm.get("external_id"),
                        "source": "tago",
                        "service": "getSttnAcctoArvlPrearngeInfoList",
                    },
                },
                self._walk("버스 하차 후 지하철 환승 도보", bus_mid.lat, bus_mid.lng, sub_mid.lat, sub_mid.lng, tw, speed),
                {
                    "mode": "subway",
                    "instruction": "지하철 승차",
                    "distance_m": int(ride2),
                    "duration_s": max(int(ride2 / 9.0), 60),
                    "start": {"lat": sub_mid.lat, "lng": sub_mid.lng},
                    "end": {"lat": sub_d.lat, "lng": sub_d.lng},
                    "transit_info": {
                        "subway_id": raw_sm.get("subway_id"),
                        "station_id": raw_sm.get("station_id") or raw_sm.get("external_id"),
                        "card_stop_id": raw_sm.get("card_stop_id") or raw_sm.get("station_id") or raw_sm.get("external_id"),
                        "station_name": station_name or None,
                        "board_station": raw_sm.get("name"),
                        "alight_station": raw_sd.get("name"),
                        "source": "seoul_subway",
                        "service": "realtimeStationArrival/ALL",
                    },
                },
                self._walk("하차역에서 목적지까지 도보", sub_d.lat, sub_d.lng, d_lat, d_lng, w2, speed),
            ],
        }

    def _walk(self, instruction, slat, slng, elat, elng, dist, speed) -> dict:
        return {
            "mode": "walk",
            "instruction": instruction,
            "distance_m": int(dist),
            "duration_s": walk_seconds(dist, speed),
            "start": {"lat": slat, "lng": slng},
            "end": {"lat": elat, "lng": elng},
        }
