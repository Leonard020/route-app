import uuid
from datetime import datetime
from typing import Optional, List, TYPE_CHECKING
from sqlalchemy import String, Integer, Double, Text, DateTime, ForeignKey, UniqueConstraint, Index
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.db.base import Base

if TYPE_CHECKING:
    from app.models.route import Route
    from app.models.step_segment import StepSegment


class RouteStep(Base):
    __tablename__ = "route_steps"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, server_default="uuid_generate_v4()"
    )
    route_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("routes.id", ondelete="CASCADE"), nullable=False
    )
    step_order: Mapped[int] = mapped_column(Integer, nullable=False)
    mode: Mapped[str] = mapped_column(String(20), nullable=False)
    instruction: Mapped[Optional[str]] = mapped_column(Text)
    distance_m: Mapped[int] = mapped_column(Integer, nullable=False)
    duration_s: Mapped[int] = mapped_column(Integer, nullable=False)
    start_lat: Mapped[float] = mapped_column(Double, nullable=False)
    start_lng: Mapped[float] = mapped_column(Double, nullable=False)
    end_lat: Mapped[float] = mapped_column(Double, nullable=False)
    end_lng: Mapped[float] = mapped_column(Double, nullable=False)
    polyline: Mapped[Optional[str]] = mapped_column(Text)
    transit_info: Mapped[Optional[dict]] = mapped_column(JSONB)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, server_default="now()"
    )

    route: Mapped["Route"] = relationship(back_populates="steps")
    segments: Mapped[List["StepSegment"]] = relationship(
        back_populates="step",
        cascade="all, delete-orphan",
        order_by="StepSegment.seg_order",
    )

    __table_args__ = (
        UniqueConstraint("route_id", "step_order", name="uq_route_steps_order"),
        Index("idx_route_steps_route", "route_id", "step_order"),
    )