import uuid
from datetime import datetime
from typing import Optional, List
from sqlalchemy import String, Text, SmallInteger, Integer, Boolean, DateTime, Index
from sqlalchemy.dialects.postgresql import UUID, ARRAY
from sqlalchemy.orm import Mapped, mapped_column
from app.db.base import Base


class SubwayRealtimeArrival(Base):
    __tablename__ = "subway_realtime_arrivals"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, server_default="uuid_generate_v4()"
    )
    recptn_dt: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    fetched_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, server_default="now()"
    )
    subway_id: Mapped[str] = mapped_column(String(10), nullable=False)
    station_id: Mapped[str] = mapped_column(String(20), nullable=False)
    station_name: Mapped[Optional[str]] = mapped_column(String(100))
    updn_line: Mapped[int] = mapped_column(SmallInteger, nullable=False)
    train_line_nm: Mapped[Optional[str]] = mapped_column(String(100))
    prev_station_id: Mapped[Optional[str]] = mapped_column(String(20))
    next_station_id: Mapped[Optional[str]] = mapped_column(String(20))
    transfer_count: Mapped[int] = mapped_column(SmallInteger, nullable=False, server_default="0")
    ord_key: Mapped[Optional[str]] = mapped_column(String(20))
    ord_updn: Mapped[Optional[str]] = mapped_column(String(1))
    ord_seq: Mapped[Optional[str]] = mapped_column(String(1))
    ord_remaining_stops: Mapped[Optional[int]] = mapped_column(SmallInteger)
    ord_dest_code: Mapped[Optional[str]] = mapped_column(String(10))
    ord_express: Mapped[Optional[str]] = mapped_column(String(1))
    transfer_line_ids: Mapped[Optional[List[str]]] = mapped_column(ARRAY(Text))
    transfer_station_ids: Mapped[Optional[List[str]]] = mapped_column(ARRAY(Text))
    train_type: Mapped[Optional[str]] = mapped_column(String(20))
    arrival_seconds: Mapped[Optional[int]] = mapped_column(Integer)
    train_no: Mapped[Optional[str]] = mapped_column(String(20))
    final_station_id: Mapped[Optional[str]] = mapped_column(String(20))
    final_station_name: Mapped[Optional[str]] = mapped_column(String(100))
    first_msg: Mapped[Optional[str]] = mapped_column(String(200))
    second_msg: Mapped[Optional[str]] = mapped_column(String(200))
    arrival_code: Mapped[Optional[int]] = mapped_column(SmallInteger)
    is_last_car: Mapped[bool] = mapped_column(Boolean, nullable=False, server_default="false")
    raw_id: Mapped[Optional[uuid.UUID]] = mapped_column(UUID(as_uuid=True))

    __table_args__ = (
        Index("idx_arrivals_station_time", "station_id", "recptn_dt"),
        Index("idx_arrivals_subway_time", "subway_id", "recptn_dt"),
        Index("idx_arrivals_train_no", "train_no", "recptn_dt"),
        Index("idx_arrivals_code", "arrival_code"),
    )
