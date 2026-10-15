from typing import Any
from sqlalchemy.dialects.postgresql import UUID as PG_UUID, JSONB as PG_JSONB
from sqlalchemy import Text

# 재사용 타입 별칭
UUIDType = PG_UUID(as_uuid=True)
JSONBType = PG_JSONB
TextArray = Text  # 배열은 별도로 postgresql.ARRAY 사용