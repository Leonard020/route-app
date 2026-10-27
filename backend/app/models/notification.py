import uuid
from datetime import datetime
from typing import Optional, TYPE_CHECKING
from sqlalchemy import String, Text, DateTime, ForeignKey, CheckConstraint, Index
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.db.base import Base

if TYPE_CHECKING:
    from app.models.user import User


class Notification(Base):
    __tablename__ = "notifications"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, server_default="uuid_generate_v4()"
    )
    user_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False
    )
    type: Mapped[str] = mapped_column(String(30), nullable=False)
    title: Mapped[str] = mapped_column(String(200), nullable=False)
    body: Mapped[Optional[str]] = mapped_column(Text)
    payload: Mapped[Optional[dict]] = mapped_column(JSONB)
    channel: Mapped[str] = mapped_column(String(20), nullable=False, server_default="push")
    status: Mapped[str] = mapped_column(String(20), nullable=False, server_default="pending")
    sent_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True))
    read_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True))
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, server_default="now()"
    )

    user: Mapped["User"] = relationship(back_populates="notifications")

    __table_args__ = (
        CheckConstraint(
            "type IN ('reroute','eta_change','depart','arrive','notice','transfer','alight')",
            name="notifications_type",
        ),
        CheckConstraint(
            "status IN ('pending','sent','failed')", name="notifications_status"
        ),
        Index("idx_noti_user_created", "user_id", "created_at"),
        Index("idx_noti_status", "status"),
    )