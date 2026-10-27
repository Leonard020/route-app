import uuid
from datetime import datetime
from typing import Optional, List, TYPE_CHECKING, Any
from sqlalchemy import String, Text, Double, Numeric, DateTime, Index
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.orm import Mapped, mapped_column, relationship
from geoalchemy2 import Geography
from app.db.base import Base

if TYPE_CHECKING:
    from app.models.favorite import Favorite
    from app.models.recent_search import RecentSearch
    from app.models.route import Route


class Place(Base):
    __tablename__ = "places"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, server_default="uuid_generate_v4()"
    )
    external_id: Mapped[Optional[str]] = mapped_column(String(100))
    standard_bus_stop_id: Mapped[Optional[str]] = mapped_column(String(20))
    ars_id: Mapped[Optional[str]] = mapped_column(String(10))
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    address: Mapped[str] = mapped_column(Text, nullable=False)
    road_address: Mapped[Optional[str]] = mapped_column(Text)
    category: Mapped[Optional[str]] = mapped_column(String(50))
    lat: Mapped[float] = mapped_column(Double, nullable=False)
    lng: Mapped[float] = mapped_column(Double, nullable=False)
    location: Mapped[Optional[Any]] = mapped_column(
        Geography(geometry_type="POINT", srid=4326)
    )
    phone: Mapped[Optional[str]] = mapped_column(String(30))
    opening_hours: Mapped[Optional[dict]] = mapped_column(JSONB)
    rating: Mapped[Optional[float]] = mapped_column(Numeric(3, 2))
    raw: Mapped[Optional[dict]] = mapped_column(JSONB)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, server_default="now()"
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, server_default="now()"
    )

    favorites: Mapped[List["Favorite"]] = relationship(back_populates="place")
    recent_searches: Mapped[List["RecentSearch"]] = relationship(back_populates="place")

    __table_args__ = (
        Index("idx_places_external_id", "external_id"),
        Index("idx_places_std_stop", "standard_bus_stop_id"),
        Index("idx_places_ars", "ars_id"),
        Index(
            "idx_places_name_trgm", "name",
            postgresql_using="gin", postgresql_ops={"name": "gin_trgm_ops"},
        ),
        Index("idx_places_location", "location", postgresql_using="gist"),
    )