import uuid
from datetime import datetime
from typing import Optional
from sqlalchemy import String, Integer, Double, Boolean, DateTime, ForeignKey, Index
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column
from app.db.base import Base


class GuidanceSession(Base):
    __tablename__ = "guidance_sessions"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, server_default="uuid_generate_v4()"
    )
    user_id: Mapped[Optional[uuid.UUID]] = mapped_column(
        UUID(as_uuid=True), ForeignKey("users.id", ondelete="SET NULL")
    )
    route_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("routes.id", ondelete="CASCADE"), nullable=False
    )
    status: Mapped[str] = mapped_column(String(20), nullable=False, server_default="active")
    current_lat: Mapped[Optional[float]] = mapped_column(Double)
    current_lng: Mapped[Optional[float]] = mapped_column(Double)
    current_step_order: Mapped[int] = mapped_column(Integer, nullable=False, server_default="1")
    remaining_duration_s: Mapped[int] = mapped_column(Integer, nullable=False, server_default="0")
    off_route: Mapped[bool] = mapped_column(Boolean, nullable=False, server_default="false")
    transfer_risk: Mapped[bool] = mapped_column(Boolean, nullable=False, server_default="false")
    started_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, server_default="now()"
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, server_default="now()"
    )
    ended_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True))

    __table_args__ = (
        Index("idx_guidance_route", "route_id"),
        Index("idx_guidance_user", "user_id", "status"),
    )
