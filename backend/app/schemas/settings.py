from typing import Literal, Optional
from pydantic import BaseModel, Field


class PreferenceOut(BaseModel):
    walk_speed: Literal["slow", "normal", "fast"]
    route_sort: Literal["fastest", "min_transfer", "min_walk"]
    alert_alight: bool
    alert_transfer: bool
    alert_minutes_before: int
    notify_enabled: bool
    max_walk_min: int
    accessibility: bool


class PreferenceUpdate(BaseModel):
    walk_speed: Optional[Literal["slow", "normal", "fast"]] = None
    route_sort: Optional[Literal["fastest", "min_transfer", "min_walk"]] = None
    alert_alight: Optional[bool] = None
    alert_transfer: Optional[bool] = None
    alert_minutes_before: Optional[int] = Field(default=None, ge=1, le=30)
    notify_enabled: Optional[bool] = None
    max_walk_min: Optional[int] = Field(default=None, ge=1, le=60)
    accessibility: Optional[bool] = None
