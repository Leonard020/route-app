import uuid
from datetime import datetime
from typing import Optional, TYPE_CHECKING
from sqlalchemy import String, SmallInteger, Text, DateTime, ForeignKey, CheckConstraint, Index
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.db.base import Base

if TYPE_CHECKING:
    from app.models.user import User
    from app.models.route import Route


class Feedback(Base):
    __tablename__ = "feedbacks"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, server_default="uuid_generate_v4()"
    )
    user_id: Mapped[Optional[uuid.UUID]] = mapped_column(
        UUID(as_uuid=True), ForeignKey("users.id", ondelete="SET NULL")
    )
    route_id: Mapped[Optional[uuid.UUID]] = mapped_column(
        UUID(as_uuid=True), ForeignKey("routes.id", ondelete="SET NULL")
    )
    type: Mapped[str] = mapped_column(String(20), nullable=False)
    rating: Mapped[Optional[int]] = mapped_column(SmallInteger)
    category: Mapped[Optional[str]] = mapped_column(String(30))
    comment: Mapped[Optional[str]] = mapped_column(Text)
    status: Mapped[str] = mapped_column(String(20), nullable=False, server_default="open")
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, server_default="now()"
    )

    user: Mapped[Optional["User"]] = relationship(back_populates="feedbacks")
    route: Mapped[Optional["Route"]] = relationship(back_populates="feedbacks")

    __table_args__ = (
        CheckConstraint("type IN ('rating','report')", name="feedbacks_type"),
        CheckConstraint("status IN ('open','reviewed','resolved')", name="feedbacks_status"),
        CheckConstraint("rating IS NULL OR (rating BETWEEN 1 AND 5)", name="feedbacks_rating"),
        Index("idx_feedbacks_route", "route_id"),
        Index("idx_feedbacks_created", "created_at"),
    )