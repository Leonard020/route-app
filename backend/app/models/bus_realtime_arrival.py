import uuid
from datetime import datetime
from typing import Optional
from sqlalchemy import String, SmallInteger, Integer, DateTime, Index
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column
from app.db.base import Base


class BusRealtimeArrival(Base):
    __tablename__ = "bus_realtime_arrivals"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, server_default="uuid_generate_v4()"
    )
    fetched_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, server_default="now()"
    )
    city_code: Mapped[str] = mapped_column(String(9), nullable=False)
    node_id: Mapped[str] = mapped_column(String(30), nullable=False)
    node_name: Mapped[Optional[str]] = mapped_column(String(30))
    route_id: Mapped[str] = mapped_column(String(30), nullable=False)
    route_no: Mapped[Optional[str]] = mapped_column(String(30))
    route_type: Mapped[Optional[str]] = mapped_column(String(10))
    arr_prev_station_cnt: Mapped[Optional[int]] = mapped_column(SmallInteger)
    vehicle_type: Mapped[Optional[str]] = mapped_column(String(10))
    arr_time_seconds: Mapped[Optional[int]] = mapped_column(Integer)
    source: Mapped[str] = mapped_column(String(20), nullable=False, server_default="tago")
    service: Mapped[str] = mapped_column(String(80), nullable=False)
    raw_id: Mapped[Optional[uuid.UUID]] = mapped_column(UUID(as_uuid=True))
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, server_default="now()"
    )

    __table_args__ = (
        Index("idx_bus_arrivals_node_time", "city_code", "node_id", "fetched_at"),
        Index("idx_bus_arrivals_route_time", "route_id", "fetched_at"),
    )
