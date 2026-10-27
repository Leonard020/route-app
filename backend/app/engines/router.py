from typing import List, Dict, Any, Optional, Tuple
from app.engines.graph import GraphProvider
from app.core.settings import settings


class Router:
    """
    대중교통 후보 경로 탐색.
    버스(TAGO)·지하철(서울시 실시간 도착정보) 구간을 후보에 포함한다.
    """

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
        city = settings.DEFAULT_BUS_CITY_CODE
        prefs = preferences or {}
        walk_factor = {"slow": 1.4, "normal": 1.0, "fast": 0.75}.get(
            prefs.get("walk_speed") or "normal", 1.0
        )

        def walk_s(base: int) -> int:
            return max(int(base * walk_factor), 1)

        bus_candidate = {
            "candidate_id": "cand-bus-1",
            "total_distance_m": 9800,
            "total_cost": 1500,
            "transfer_count": 0,
            "walk_distance_m": 700,
            "carbon_g": 280,
            "polyline": None,
            "segments": [
                {"distance_m": 400, "road_type": "walk", "congestion": 1},
                {"distance_m": 8700, "road_type": "bus", "congestion": 2},
                {"distance_m": 700, "road_type": "walk", "congestion": 1},
            ],
            "steps": [
                {
                    "mode": "walk",
                    "instruction": "출발지에서 버스 정류장까지 도보",
                    "distance_m": 400,
                    "duration_s": walk_s(320),
                    "start": {"lat": o_lat, "lng": o_lng},
                    "end": {"lat": o_lat + 0.001, "lng": o_lng + 0.001},
                },
                {
                    "mode": "bus",
                    "instruction": "버스 승차",
                    "distance_m": 8700,
                    "duration_s": 1500,
                    "start": {"lat": o_lat + 0.001, "lng": o_lng + 0.001},
                    "end": {"lat": d_lat - 0.001, "lng": d_lng - 0.001},
                    "transit_info": {
                        "city_code": city,
                        "node_id": None,
                        "route_id": None,
                        "route_no": None,
                        "source": "tago",
                        "service": "getSttnAcctoArvlPrearngeInfoList",
                    },
                },
                {
                    "mode": "walk",
                    "instruction": "하차 정류장에서 목적지까지 도보",
                    "distance_m": 700,
                    "duration_s": walk_s(560),
                    "start": {"lat": d_lat - 0.001, "lng": d_lng - 0.001},
                    "end": {"lat": d_lat, "lng": d_lng},
                },
            ],
        }

        subway_candidate = {
            "candidate_id": "cand-subway-1",
            "total_distance_m": 11200,
            "total_cost": 1500,
            "transfer_count": 1,
            "walk_distance_m": 900,
            "carbon_g": 160,
            "polyline": None,
            "segments": [
                {"distance_m": 500, "road_type": "walk", "congestion": 1},
                {"distance_m": 9800, "road_type": "subway", "congestion": 1},
                {"distance_m": 900, "road_type": "walk", "congestion": 1},
            ],
            "steps": [
                {
                    "mode": "walk",
                    "instruction": "출발지에서 지하철역까지 도보",
                    "distance_m": 500,
                    "duration_s": walk_s(400),
                    "start": {"lat": o_lat, "lng": o_lng},
                    "end": {"lat": o_lat + 0.002, "lng": o_lng + 0.002},
                },
                {
                    "mode": "subway",
                    "instruction": "지하철 승차",
                    "distance_m": 9800,
                    "duration_s": 1320,
                    "start": {"lat": o_lat + 0.002, "lng": o_lng + 0.002},
                    "end": {"lat": d_lat - 0.002, "lng": d_lng - 0.002},
                    "transit_info": {
                        "subway_id": None,
                        "station_id": None,
                        "station_name": None,
                        "updn_line": None,
                        "source": "seoul_subway",
                        "service": "realtimeStationArrival/ALL",
                    },
                },
                {
                    "mode": "walk",
                    "instruction": "하차역에서 목적지까지 도보",
                    "distance_m": 900,
                    "duration_s": walk_s(720),
                    "start": {"lat": d_lat - 0.002, "lng": d_lng - 0.002},
                    "end": {"lat": d_lat, "lng": d_lng},
                },
            ],
        }

        mixed = {
            "candidate_id": "cand-mixed-1",
            "total_distance_m": 10800,
            "total_cost": 3000,
            "transfer_count": 1,
            "walk_distance_m": 1100,
            "carbon_g": 220,
            "polyline": None,
            "segments": [
                {"distance_m": 400, "road_type": "walk", "congestion": 1},
                {"distance_m": 4200, "road_type": "bus", "congestion": 2},
                {"distance_m": 300, "road_type": "walk", "congestion": 1},
                {"distance_m": 4800, "road_type": "subway", "congestion": 1},
                {"distance_m": 1100, "road_type": "walk", "congestion": 1},
            ],
            "steps": [
                {
                    "mode": "walk",
                    "instruction": "출발지에서 버스 정류장까지 도보",
                    "distance_m": 400,
                    "duration_s": walk_s(320),
                    "start": {"lat": o_lat, "lng": o_lng},
                    "end": {"lat": o_lat + 0.001, "lng": o_lng},
                },
                {
                    "mode": "bus",
                    "instruction": "버스로 환승역 이동",
                    "distance_m": 4200,
                    "duration_s": 900,
                    "start": {"lat": o_lat + 0.001, "lng": o_lng},
                    "end": {"lat": (o_lat + d_lat) / 2, "lng": (o_lng + d_lng) / 2},
                    "transit_info": {
                        "city_code": city,
                        "node_id": None,
                        "route_id": None,
                        "source": "tago",
                        "service": "getSttnAcctoArvlPrearngeInfoList",
                    },
                },
                {
                    "mode": "walk",
                    "instruction": "버스 하차 후 지하철 환승 도보",
                    "distance_m": 300,
                    "duration_s": walk_s(240),
                    "start": {"lat": (o_lat + d_lat) / 2, "lng": (o_lng + d_lng) / 2},
                    "end": {"lat": (o_lat + d_lat) / 2 + 0.0005, "lng": (o_lng + d_lng) / 2},
                },
                {
                    "mode": "subway",
                    "instruction": "지하철 승차",
                    "distance_m": 4800,
                    "duration_s": 720,
                    "start": {"lat": (o_lat + d_lat) / 2 + 0.0005, "lng": (o_lng + d_lng) / 2},
                    "end": {"lat": d_lat - 0.001, "lng": d_lng - 0.001},
                    "transit_info": {
                        "source": "seoul_subway",
                        "service": "realtimeStationArrival/ALL",
                    },
                },
                {
                    "mode": "walk",
                    "instruction": "하차역에서 목적지까지 도보",
                    "distance_m": 1100,
                    "duration_s": walk_s(880),
                    "start": {"lat": d_lat - 0.001, "lng": d_lng - 0.001},
                    "end": {"lat": d_lat, "lng": d_lng},
                },
            ],
        }
        return [bus_candidate, subway_candidate, mixed][: max(top_k, 3)]
