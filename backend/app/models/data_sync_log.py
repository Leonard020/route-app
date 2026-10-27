import uuid
from datetime import datetime
from typing import Optional
from sqlalchemy import String, Text, Integer, DateTime, Index
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column
from app.db.base import Base


class DataSyncLog(Base):
    __tablename__ = "data_sync_logs"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, server_default="uuid_generate_v4()"
    )
    source: Mapped[str] = mapped_column(String(50), nullable=False)
    service: Mapped[str] = mapped_column(String(100), nullable=False)
    started_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    finished_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True))
    status: Mapped[str] = mapped_column(String(20), nullable=False)
    items_fetched: Mapped[int] = mapped_column(Integer, nullable=False, server_default="0")
    items_saved: Mapped[int] = mapped_column(Integer, nullable=False, server_default="0")
    items_failed: Mapped[int] = mapped_column(Integer, nullable=False, server_default="0")
    error_code: Mapped[Optional[str]] = mapped_column(String(20))
    error_message: Mapped[Optional[str]] = mapped_column(Text)

    __table_args__ = (
        Index("idx_sync_source_started", "source", "started_at"),
    )
