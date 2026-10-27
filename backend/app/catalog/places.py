from dataclasses import dataclass, field
from uuid import uuid5, NAMESPACE_URL
from app.domain.geo import haversine_m


@dataclass
class CatalogPlace:
    name: str
    address: str
    category: str
    lat: float
    lng: float
    external_id: str | None = None
    raw: dict = field(default_factory=dict)

    @property
    def id(self):
        return uuid5(NAMESPACE_URL, f"place:{self.name}:{self.lat}:{self.lng}")


CATALOG: list[CatalogPlace] = [
    CatalogPlace("강남역", "서울 강남구 강남대로 396", "subway", 37.4979, 127.0276, "1002000222",
                 {"subway_id": "1002", "station_id": "1002000222", "station_name": "강남"}),
    CatalogPlace("성수역", "서울 성동구 아차산로 100", "subway", 37.5446, 127.0559, "1002000211",
                 {"subway_id": "1002", "station_id": "1002000211", "station_name": "성수"}),
    CatalogPlace("서울역", "서울 중구 한강대로 405", "subway", 37.5547, 126.9707, "1001000100",
                 {"subway_id": "1001", "station_id": "1001000100", "station_name": "서울"}),
    CatalogPlace("시청역", "서울 중구 세종대로 110", "subway", 37.5651, 126.9770, "1001000132",
                 {"subway_id": "1001", "station_id": "1001000132", "station_name": "시청"}),
    CatalogPlace("홍대입구역", "서울 마포구 양화로 160", "subway", 37.5572, 126.9254, "1002000239",
                 {"subway_id": "1002", "station_id": "1002000239", "station_name": "홍대입구"}),
    CatalogPlace("잠실역", "서울 송파구", "subway", 37.5133, 127.1001, "1002000216",
                 {"subway_id": "1002", "station_name": "잠실"}),
    CatalogPlace("여의도역", "서울 영등포구", "subway", 37.5216, 126.9242, None,
                 {"subway_id": "1005", "station_name": "여의도"}),
    CatalogPlace("건대입구역", "서울 광진구", "subway", 37.5404, 127.0692, None,
                 {"subway_id": "1002", "station_name": "건대입구"}),
    CatalogPlace("강남역.강남역버스환승센터", "서울 강남구 강남대로 396", "bus", 37.4982, 127.0278, "GGB204000376",
                 {"city_code": "11", "node_id": "GGB204000376"}),
    CatalogPlace("서울역버스환승센터", "서울 중구 한강대로 405", "bus", 37.5551, 126.9710, "GGB115000001",
                 {"city_code": "11", "node_id": "GGB115000001"}),
    CatalogPlace("성수역버스정류장", "서울 성동구", "bus", 37.5449, 127.0562, "GGB104000211",
                 {"city_code": "11", "node_id": "GGB104000211"}),
    CatalogPlace("회사 (역삼동)", "즐겨찾기", "place", 37.5007, 127.0366),
    CatalogPlace("집 (망원동)", "즐겨찾기", "place", 37.5560, 126.9100),
    CatalogPlace("COEX 스타필드", "서울 강남구 삼성동", "place", 37.5116, 127.0594),
    CatalogPlace("서울숲", "서울 성동구 성수동", "place", 37.5444, 127.0374),
    CatalogPlace("경복궁", "서울 종로구 사직로", "place", 37.5796, 126.9770),
]


def search_catalog(q: str, limit: int = 20) -> list[CatalogPlace]:
    needle = (q or "").strip()
    if not needle:
        return CATALOG[:limit]
    return [p for p in CATALOG if needle in p.name or needle in p.address][:limit]


def nearest_catalog(lat: float, lng: float, category: str | None = None, max_m: float = 2000):
    rows = [p for p in CATALOG if category is None or p.category == category]
    if not rows:
        return None
    best = min(rows, key=lambda p: haversine_m(lat, lng, p.lat, p.lng))
    if haversine_m(lat, lng, best.lat, best.lng) > max_m:
        return None
    return best
