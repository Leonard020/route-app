from datetime import datetime
from typing import Optional, Literal
from pydantic import BaseModel, Field


class LatLng(BaseModel):
    lat: float
    lng: float
    place_id: Optional[str] = None
    name: Optional[str] = None


class RoutePreferences(BaseModel):
    preferred_mode: Optional[str] = "transit"
    eco_priority: bool = False
    max_walk_min: int = 20
    accessibility: bool = False
    walk_speed: Literal["slow", "normal", "fast"] = "normal"
    route_sort: Literal["fastest", "min_transfer", "min_walk"] = "fastest"


class RouteOptions(BaseModel):
    top_n: int = 3
    include_polyline: bool = False
    include_steps: bool = True
    refresh: bool = False


class RouteRecommendRequest(BaseModel):
    origin: LatLng
    destination: LatLng
    mode: str = "transit"
    depart_at: Optional[datetime] = None
    preferences: Optional[RoutePreferences] = None
    options: Optional[RouteOptions] = None


class RouteSummary(BaseModel):
    total_distance_m: int
    total_duration_s: int
    total_cost: int = 0
    transfer_count: int = 0
    walk_distance_m: int = 0
    carbon_g: int = 0
    eta: Optional[datetime] = None
    realtime_used: bool = False
    last_fetched_at: Optional[datetime] = None
    walk_duration_s: int = 0
    wait_duration_s: int = 0
    vehicle_duration_s: int = 0
    transfer_walk_s: int = 0
    transfer_wait_s: int = 0
    label: Optional[str] = None
    time_basis: Optional[str] = None


class RouteStep(BaseModel):
    step_order: Optional[int] = None
    mode: str
    instruction: Optional[str] = None
    distance_m: int
    duration_s: int
    start_lat: Optional[float] = None
    start_lng: Optional[float] = None
    end_lat: Optional[float] = None
    end_lng: Optional[float] = None
    start: Optional[dict] = None
    end: Optional[dict] = None
    polyline: Optional[str] = None
    transit_info: Optional[dict] = None
    segments: list[dict] = Field(default_factory=list)


class RouteOut(BaseModel):
    route_id: str
    rank: int = 1
    mode: str
    summary: RouteSummary
    polyline: Optional[str] = None
    steps: list[RouteStep] = Field(default_factory=list)
    predictor_version: Optional[str] = None
    score: Optional[float] = None
    reason: Optional[str] = None


class RouteRecommendResponse(BaseModel):
    routes: list[RouteOut]


class RerouteRequest(BaseModel):
    current_location: LatLng
    reason: Literal["traffic", "incident", "deviation", "manual"] = "manual"


class RerouteDelta(BaseModel):
    duration_s: int
    distance_m: int
    cost: int = 0


class RerouteResponse(BaseModel):
    route_id: str
    changed: bool
    delta: RerouteDelta
    route: RouteOut
    reason_text: str


class FeedbackCreate(BaseModel):
    type: Literal["rating", "report"] = "rating"
    rating: Optional[int] = Field(default=None, ge=1, le=5)
    category: Optional[str] = None
    comment: Optional[str] = None
