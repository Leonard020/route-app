import uuid
from datetime import date, datetime
from typing import Optional
from sqlalchemy import String, Integer, SmallInteger, Date, DateTime, UniqueConstraint, Index, CheckConstraint
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column
from app.db.base import Base


class StationTransferFlow(Base):
    """서울시 정류장별 사용자유형별 환승 승객수 및 환승시간."""

    __tablename__ = "station_transfer_flows"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, server_default="uuid_generate_v4()"
    )
    base_date: Mapped[date] = mapped_column(Date, nullable=False)
    alight_stop_id: Mapped[str] = mapped_column(String(20), nullable=False)
    board_stop_id: Mapped[str] = mapped_column(String(20), nullable=False)
    hour: Mapped[int] = mapped_column(SmallInteger, nullable=False)
    transfer_count_total: Mapped[int] = mapped_column(Integer, nullable=False, server_default="0")
    transfer_count_general: Mapped[int] = mapped_column(Integer, nullable=False, server_default="0")
    transfer_count_child: Mapped[int] = mapped_column(Integer, nullable=False, server_default="0")
    transfer_count_youth: Mapped[int] = mapped_column(Integer, nullable=False, server_default="0")
    transfer_count_senior: Mapped[int] = mapped_column(Integer, nullable=False, server_default="0")
    transfer_count_disabled: Mapped[int] = mapped_column(Integer, nullable=False, server_default="0")
    transfer_time_avg_s: Mapped[Optional[int]] = mapped_column(Integer)
    transfer_time_avg_general_s: Mapped[Optional[int]] = mapped_column(Integer)
    transfer_time_avg_child_s: Mapped[Optional[int]] = mapped_column(Integer)
    transfer_time_avg_youth_s: Mapped[Optional[int]] = mapped_column(Integer)
    transfer_time_avg_senior_s: Mapped[Optional[int]] = mapped_column(Integer)
    transfer_time_avg_disabled_s: Mapped[Optional[int]] = mapped_column(Integer)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, server_default="now()"
    )

    __table_args__ = (
        UniqueConstraint(
            "base_date", "alight_stop_id", "board_stop_id", "hour",
            name="uq_transfer_flow_date_pair_hour",
        ),
        CheckConstraint("hour BETWEEN 0 AND 23", name="ck_transfer_hour"),
        Index("idx_transfer_flow_pair", "alight_stop_id", "board_stop_id", "hour"),
        Index("idx_transfer_flow_alight", "alight_stop_id", "hour"),
    )
