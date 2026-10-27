import uuid
from datetime import datetime
from typing import Optional
from sqlalchemy import String, Text, SmallInteger, Integer, DateTime, Index
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.orm import Mapped, mapped_column
from app.db.base import Base


class RawPublicData(Base):
    __tablename__ = "raw_public_data"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, server_default="uuid_generate_v4()"
    )
    source: Mapped[str] = mapped_column(String(50), nullable=False)
    service: Mapped[str] = mapped_column(String(100), nullable=False)
    request_url: Mapped[Optional[str]] = mapped_column(Text)
    request_params: Mapped[Optional[dict]] = mapped_column(JSONB)
    http_status: Mapped[Optional[int]] = mapped_column(SmallInteger)
    content_type: Mapped[Optional[str]] = mapped_column(String(50))
    body: Mapped[Optional[str]] = mapped_column(Text)
    result_code: Mapped[Optional[str]] = mapped_column(String(20))
    result_message: Mapped[Optional[str]] = mapped_column(String(500))
    record_count: Mapped[Optional[int]] = mapped_column(Integer)
    fetched_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, server_default="now()"
    )
    parsed_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True))
    parse_error: Mapped[Optional[str]] = mapped_column(Text)

    __table_args__ = (
        Index("idx_raw_source_fetched", "source", "fetched_at"),
        Index("idx_raw_result_code", "result_code"),
    )
