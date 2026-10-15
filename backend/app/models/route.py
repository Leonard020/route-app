import uuid
from datetime import datetime
from typing import Optional, List, TYPE_CHECKING
from sqlalchemy import String, Integer, Double, Text, DateTime, ForeignKey, CheckConstraint, Index
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.db.base import Base

if TYPE_CHECKING:
    from app.models.user import User
    from app.models.route_step import RouteStep
    from app.models.feedback import Feedback
    from app.models.prediction import Prediction


class Route(Base):
    __tablename__ = "routes"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, server_default="uuid_generate_v4()"
    )
    user_id: Mapped[Optional[uuid.UUID]] = mapped_column(
        UUID(as_uuid=True), ForeignKey("users.id", ondelete="SET NULL")
    )
    origin_place_id: Mapped[Optional[uuid.UUID]] = mapped_column(
        UUID(as_uuid=True), ForeignKey("places.id", ondelete="SET NULL")
    )
    dest_place_id: Mapped[Optional[uuid.UUID]] = mapped_column(
        UUID(as_uuid=True), ForeignKey("places.id", ondelete="SET NULL")
    )
    origin_lat: Mapped[float] = mapped_column(Double, nullable=False)
    origin_lng: Mapped[float] = mapped_column(Double, nullable=False)
    dest_lat: Mapped[float] = mapped_column(Double, nullable=False)
    dest_lng: Mapped[float] = mapped_column(Double, nullable=False)
    mode: Mapped[str] = mapped_column(String(20), nullable=False)
    preference_snapshot: Mapped[Optional[dict]] = mapped_column(JSONB)
    total_distance_m: Mapped[int] = mapped_column(Integer, nullable=False)
    total_duration_s: Mapped[int] = mapped_column(Integer, nullable=False)
    total_cost: Mapped[int] = mapped_column(Integer, nullable=False, server_default="0")
    transfer_count: Mapped[int] = mapped_column(Integer, nullable=False, server_default="0")
    walk_distance_m: Mapped[int] = mapped_column(Integer, nullable=False, server_default="0")
    carbon_g: Mapped[int] = mapped_column(Integer, nullable=False, server_default="0")
    eta: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True))
    polyline: Mapped[Optional[str]] = mapped_column(Text)
    status: Mapped[str] = mapped_column(String(20), nullable=False, server_default="active")
    predictor_version: Mapped[Optional[str]] = mapped_column(String(30))
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, server_default="now()"
    )

    user: Mapped[Optional["User"]] = relationship(back_populates="routes")
    steps: Mapped[List["RouteStep"]] = relationship(
        back_populates="route",
        cascade="all, delete-orphan",
        order_by="RouteStep.step_order",
    )
    feedbacks: Mapped[List["Feedback"]] = relationship(back_populates="route")
    predictions: Mapped[List["Prediction"]] = relationship(back_populates="route")

    __table_args__ = (
        CheckConstraint("mode IN ('walk','car','transit','bike','multi')", name="routes_mode"),
        CheckConstraint("status IN ('active','expired','rerouted')", name="routes_status"),
        Index("idx_routes_user_created", "user_id", "created_at"),
        Index("idx_routes_status", "status"),
    )