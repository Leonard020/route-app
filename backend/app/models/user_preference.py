import uuid
from datetime import datetime, time
from typing import Optional, TYPE_CHECKING
from sqlalchemy import String, Boolean, Integer, Time, DateTime, ForeignKey, CheckConstraint
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.db.base import Base

if TYPE_CHECKING:
    from app.models.user import User


class UserPreference(Base):
    __tablename__ = "user_preferences"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, server_default="uuid_generate_v4()"
    )
    user_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False, unique=True,
    )
    preferred_mode: Mapped[str] = mapped_column(String(20), nullable=False, server_default="transit")
    avoid_highway: Mapped[bool] = mapped_column(Boolean, nullable=False, server_default="false")
    avoid_toll: Mapped[bool] = mapped_column(Boolean, nullable=False, server_default="false")
    accessibility: Mapped[bool] = mapped_column(Boolean, nullable=False, server_default="false")
    eco_priority: Mapped[bool] = mapped_column(Boolean, nullable=False, server_default="false")
    max_walk_min: Mapped[int] = mapped_column(Integer, nullable=False, server_default="20")
    notify_enabled: Mapped[bool] = mapped_column(Boolean, nullable=False, server_default="true")
    walk_speed: Mapped[str] = mapped_column(String(20), nullable=False, server_default="normal")
    route_sort: Mapped[str] = mapped_column(String(20), nullable=False, server_default="fastest")
    alert_alight: Mapped[bool] = mapped_column(Boolean, nullable=False, server_default="true")
    alert_transfer: Mapped[bool] = mapped_column(Boolean, nullable=False, server_default="true")
    alert_minutes_before: Mapped[int] = mapped_column(Integer, nullable=False, server_default="3")
    dnd_start: Mapped[Optional[time]] = mapped_column(Time)
    dnd_end: Mapped[Optional[time]] = mapped_column(Time)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, server_default="now()"
    )

    user: Mapped["User"] = relationship(back_populates="preferences")

    __table_args__ = (
        CheckConstraint(
            "preferred_mode IN ('walk','car','transit','bike','multi')",
            name="pref_mode",
        ),
        CheckConstraint(
            "walk_speed IN ('slow','normal','fast')",
            name="pref_walk_speed",
        ),
        CheckConstraint(
            "route_sort IN ('fastest','min_transfer','min_walk')",
            name="pref_route_sort",
        ),
    )