import uuid
from datetime import datetime
from typing import Optional, Any
from sqlalchemy import String, Integer, Boolean, Double, DateTime, Index
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column
from geoalchemy2 import Geography
from app.db.base import Base


class SubwayStation(Base):
    __tablename__ = "subway_stations"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, server_default="uuid_generate_v4()"
    )
    station_id: Mapped[str] = mapped_column(String(20), nullable=False, unique=True)
    card_stop_id: Mapped[Optional[str]] = mapped_column(String(20))
    subway_id: Mapped[str] = mapped_column(String(10), nullable=False)
    line_name: Mapped[Optional[str]] = mapped_column(String(50))
    station_code: Mapped[Optional[str]] = mapped_column(String(10))
    station_name: Mapped[str] = mapped_column(String(100), nullable=False)
    station_name_norm: Mapped[Optional[str]] = mapped_column(String(100))
    prev_station_id: Mapped[Optional[str]] = mapped_column(String(20))
    next_station_id: Mapped[Optional[str]] = mapped_column(String(20))
    transfer_count: Mapped[int] = mapped_column(Integer, nullable=False, server_default="0")
    is_transfer: Mapped[bool] = mapped_column(Boolean, nullable=False, server_default="false")
    lat: Mapped[Optional[float]] = mapped_column(Double)
    lng: Mapped[Optional[float]] = mapped_column(Double)
    location: Mapped[Optional[Any]] = mapped_column(
        Geography(geometry_type="POINT", srid=4326)
    )
    place_id: Mapped[Optional[uuid.UUID]] = mapped_column(UUID(as_uuid=True))
    display_order: Mapped[Optional[int]] = mapped_column(Integer)
    is_active: Mapped[bool] = mapped_column(Boolean, nullable=False, server_default="true")
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, server_default="now()"
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, server_default="now()"
    )

    __table_args__ = (
        Index("idx_stations_subway", "subway_id", "display_order"),
        Index("idx_stations_place", "place_id"),
        Index("idx_stations_card_stop", "card_stop_id"),
    )
