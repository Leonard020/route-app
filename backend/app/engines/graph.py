from typing import Optional, List, Tuple
from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession
from app.db.session import get_db


class GraphProvider:
    """
    경로 탐색용 그래프 로더.
    실제 구현에서는 도로망/대중교통망 데이터를 로드.
    """

    def __init__(self, db: AsyncSession = Depends(get_db)):
        self.db = db

    async def neighbors(
        self, node_id: str, mode: str
    ) -> List[Tuple[str, float, dict]]:
        # (neighbor_id, cost, meta)
        # MVP: 더미. 실제로는 DB/캐시에서 조회.
        return []

    async def nearest_node(self, lat: float, lng: float) -> Optional[str]:
        return None