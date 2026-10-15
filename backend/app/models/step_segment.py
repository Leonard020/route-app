import uuid
from typing import Optional, TYPE_CHECKING
from sqlalchemy import String, Integer, SmallInteger, Text, ForeignKey, UniqueConstraint, Index
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.db.base import Base

if TYPE_CHECKING:
    from app.models.route_step import RouteStep


class StepSegment(Base):
    __tablename__ = "step_segments"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, server_default="uuid_generate_v4()"
    )
    step_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("route_steps.id", ondelete="CASCADE"), nullable=False
    )
    seg_order: Mapped[int] = mapped_column(Integer, nullable=False)
    distance_m: Mapped[int] = mapped_column(Integer, nullable=False)
    duration_s: Mapped[int] = mapped_column(Integer, nullable=False)
    congestion: Mapped[Optional[int]] = mapped_column(SmallInteger)
    road_type: Mapped[Optional[str]] = mapped_column(String(20))
    polyline: Mapped[Optional[str]] = mapped_column(Text)

    step: Mapped["RouteStep"] = relationship(back_populates="segments")

    __table_args__ = (
        UniqueConstraint("step_id", "seg_order", name="uq_step_segments_order"),
        Index("idx_step_segments_step", "step_id", "seg_order"),
    )