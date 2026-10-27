import uuid
from datetime import datetime
from typing import Optional
from sqlalchemy import String, Integer, DateTime, UniqueConstraint, Index
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column
from app.db.base import Base


class SubwayStationTransfer(Base):
    __tablename__ = "subway_station_transfers"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, server_default="uuid_generate_v4()"
    )
    station_id: Mapped[str] = mapped_column(String(20), nullable=False)
    transfer_subway_id: Mapped[str] = mapped_column(String(10), nullable=False)
    transfer_station_id: Mapped[str] = mapped_column(String(20), nullable=False)
    avg_transfer_s: Mapped[Optional[int]] = mapped_column(Integer)
    sample_transfers: Mapped[Optional[int]] = mapped_column(Integer)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, server_default="now()"
    )

    __table_args__ = (
        UniqueConstraint("station_id", "transfer_station_id", name="uq_transfers_station"),
        Index("idx_transfers_station", "station_id"),
    )
