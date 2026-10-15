from typing import List, Dict, Any, Optional, Tuple
from app.engines.graph import GraphProvider


class Router:
    """
    A*/Dijkstra 기반 후보 경로 탐색.
    MVP에서는 외부 지도 API 어댑터로 대체 가능.
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
        """
        후보 경로 목록 반환.
        각 후보: {
          candidate_id, segments[], steps[], total_distance_m,
          total_cost, transfer_count, walk_distance_m, carbon_g, polyline
        }
        """
        # MVP 스텁: 외부 지도 API 어댑터로 위임 예정
        # 더미 후보 2개 반환
        return [
            {
                "candidate_id": "cand-1",
                "total_distance_m": 12000,
                "total_cost": 1450,
                "transfer_count": 1,
                "walk_distance_m": 800,
                "carbon_g": 320,
                "polyline": None,
                "segments": [
                    {"distance_m": 1000, "road_type": "urban", "congestion": 2},
                    {"distance_m": 11000, "road_type": "highway", "congestion": 1},
                ],
                "steps": [
                    {
                        "mode": "walk",
                        "instruction": "출발지에서 도보",
                        "distance_m": 300,
                        "duration_s": 240,
                        "start": {"lat": origin[0], "lng": origin[1]},
                        "end": {"lat": origin[0] + 0.001, "lng": origin[1] + 0.001},
                    }
                ],
            },
            {
                "candidate_id": "cand-2",
                "total_distance_m": 13500,
                "total_cost": 0,
                "transfer_count": 2,
                "walk_distance_m": 1200,
                "carbon_g": 120,
                "polyline": None,
                "segments": [
                    {"distance_m": 2000, "road_type": "local", "congestion": 3},
                ],
                "steps": [
                    {
                        "mode": "walk",
                        "instruction": "도보",
                        "distance_m": 500,
                        "duration_s": 400,
                        "start": {"lat": origin[0], "lng": origin[1]},
                        "end": {"lat": origin[0] + 0.002, "lng": origin[1] + 0.002},
                    }
                ],
            },
        ]