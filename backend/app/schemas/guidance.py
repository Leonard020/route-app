from datetime import datetime
from typing import Optional
from pydantic import BaseModel
from app.schemas.route import LatLng


class GuidanceStartRequest(BaseModel):
    route_id: str
    current_location: Optional[LatLng] = None
    location_permission: bool = True
    notify_permission: bool = True


class GuidanceTickRequest(BaseModel):
    current_location: LatLng
    current_step_order: Optional[int] = None


class GuidanceOut(BaseModel):
    session_id: str
    route_id: str
    status: str
    current_step_order: int
    remaining_duration_s: int
    eta: Optional[datetime] = None
    off_route: bool = False
    transfer_risk: bool = False
    message: Optional[str] = None
    next_action: Optional[str] = None
    alerts: list[str] = []
