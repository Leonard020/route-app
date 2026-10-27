import uuid
from datetime import date, datetime
from typing import Optional
from sqlalchemy import String, Integer, Date, DateTime, UniqueConstraint, Index
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column
from app.db.base import Base


class BusHourlyBoarding(Base):
    """버스노선별 정류장별 시간대별 승하차 인원 (서울시)."""

    __tablename__ = "bus_hourly_boardings"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, server_default="uuid_generate_v4()"
    )
    use_ym: Mapped[str] = mapped_column(String(6), nullable=False)
    route_no: Mapped[str] = mapped_column(String(20), nullable=False)
    route_name: Mapped[Optional[str]] = mapped_column(String(100))
    standard_stop_id: Mapped[str] = mapped_column(String(20), nullable=False)
    ars_id: Mapped[Optional[str]] = mapped_column(String(10))
    stop_name: Mapped[Optional[str]] = mapped_column(String(100))
    boarding_h00: Mapped[Optional[int]] = mapped_column(Integer)
    alight_h00: Mapped[Optional[int]] = mapped_column(Integer)
    boarding_h01: Mapped[Optional[int]] = mapped_column(Integer)
    alight_h01: Mapped[Optional[int]] = mapped_column(Integer)
    boarding_h02: Mapped[Optional[int]] = mapped_column(Integer)
    alight_h02: Mapped[Optional[int]] = mapped_column(Integer)
    boarding_h03: Mapped[Optional[int]] = mapped_column(Integer)
    alight_h03: Mapped[Optional[int]] = mapped_column(Integer)
    boarding_h04: Mapped[Optional[int]] = mapped_column(Integer)
    alight_h04: Mapped[Optional[int]] = mapped_column(Integer)
    boarding_h05: Mapped[Optional[int]] = mapped_column(Integer)
    alight_h05: Mapped[Optional[int]] = mapped_column(Integer)
    boarding_h06: Mapped[Optional[int]] = mapped_column(Integer)
    alight_h06: Mapped[Optional[int]] = mapped_column(Integer)
    boarding_h07: Mapped[Optional[int]] = mapped_column(Integer)
    alight_h07: Mapped[Optional[int]] = mapped_column(Integer)
    boarding_h08: Mapped[Optional[int]] = mapped_column(Integer)
    alight_h08: Mapped[Optional[int]] = mapped_column(Integer)
    boarding_h09: Mapped[Optional[int]] = mapped_column(Integer)
    alight_h09: Mapped[Optional[int]] = mapped_column(Integer)
    boarding_h10: Mapped[Optional[int]] = mapped_column(Integer)
    alight_h10: Mapped[Optional[int]] = mapped_column(Integer)
    boarding_h11: Mapped[Optional[int]] = mapped_column(Integer)
    alight_h11: Mapped[Optional[int]] = mapped_column(Integer)
    boarding_h12: Mapped[Optional[int]] = mapped_column(Integer)
    alight_h12: Mapped[Optional[int]] = mapped_column(Integer)
    boarding_h13: Mapped[Optional[int]] = mapped_column(Integer)
    alight_h13: Mapped[Optional[int]] = mapped_column(Integer)
    boarding_h14: Mapped[Optional[int]] = mapped_column(Integer)
    alight_h14: Mapped[Optional[int]] = mapped_column(Integer)
    boarding_h15: Mapped[Optional[int]] = mapped_column(Integer)
    alight_h15: Mapped[Optional[int]] = mapped_column(Integer)
    boarding_h16: Mapped[Optional[int]] = mapped_column(Integer)
    alight_h16: Mapped[Optional[int]] = mapped_column(Integer)
    boarding_h17: Mapped[Optional[int]] = mapped_column(Integer)
    alight_h17: Mapped[Optional[int]] = mapped_column(Integer)
    boarding_h18: Mapped[Optional[int]] = mapped_column(Integer)
    alight_h18: Mapped[Optional[int]] = mapped_column(Integer)
    boarding_h19: Mapped[Optional[int]] = mapped_column(Integer)
    alight_h19: Mapped[Optional[int]] = mapped_column(Integer)
    boarding_h20: Mapped[Optional[int]] = mapped_column(Integer)
    alight_h20: Mapped[Optional[int]] = mapped_column(Integer)
    boarding_h21: Mapped[Optional[int]] = mapped_column(Integer)
    alight_h21: Mapped[Optional[int]] = mapped_column(Integer)
    boarding_h22: Mapped[Optional[int]] = mapped_column(Integer)
    alight_h22: Mapped[Optional[int]] = mapped_column(Integer)
    boarding_h23: Mapped[Optional[int]] = mapped_column(Integer)
    alight_h23: Mapped[Optional[int]] = mapped_column(Integer)
    transport_type_code: Mapped[Optional[str]] = mapped_column(String(10))
    transport_type_name: Mapped[Optional[str]] = mapped_column(String(50))
    registered_on: Mapped[Optional[date]] = mapped_column(Date)
    place_id: Mapped[Optional[uuid.UUID]] = mapped_column(UUID(as_uuid=True))
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, server_default="now()"
    )

    __table_args__ = (
        UniqueConstraint("use_ym", "route_no", "standard_stop_id", name="uq_bus_hourly_ym_route_stop"),
        Index("idx_bus_hourly_stop", "standard_stop_id", "use_ym"),
        Index("idx_bus_hourly_route", "route_no", "use_ym"),
        Index("idx_bus_hourly_place", "place_id"),
    )

    def counts_at(self, hour: int) -> tuple[int, int]:
        h = max(0, min(23, int(hour)))
        board = getattr(self, f"boarding_h{h:02d}") or 0
        alight = getattr(self, f"alight_h{h:02d}") or 0
        return int(board), int(alight)
