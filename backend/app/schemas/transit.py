from datetime import datetime
from typing import Optional
from pydantic import BaseModel, Field


class BusArrivalItem(BaseModel):
    node_id: str
    node_name: Optional[str] = None
    route_id: str
    route_no: Optional[str] = None
    route_type: Optional[str] = None
    arr_prev_station_cnt: Optional[int] = None
    vehicle_type: Optional[str] = None
    arr_time_seconds: Optional[int] = None
    city_code: str
    stale: bool = False


class BusArrivalResponse(BaseModel):
    city_code: str
    node_id: str
    route_id: Optional[str] = None
    fetched_at: datetime
    last_fetched_at: Optional[datetime] = None
    result_code: str
    result_message: str
    total_count: int
    items: list[BusArrivalItem]
    realtime: bool = True


class CityCodeItem(BaseModel):
    city_code: str
    city_name: str


class SubwayArrivalItem(BaseModel):
    subway_id: str
    line_name: Optional[str] = None
    station_id: str
    station_name: Optional[str] = None
    updn_line: int
    train_line_nm: Optional[str] = None
    prev_station_id: Optional[str] = None
    next_station_id: Optional[str] = None
    transfer_count: int = 0
    ord_key: Optional[str] = None
    train_type: Optional[str] = None
    arrival_seconds: Optional[int] = None
    train_no: Optional[str] = None
    final_station_id: Optional[str] = None
    final_station_name: Optional[str] = None
    recptn_dt: Optional[datetime] = None
    first_msg: Optional[str] = None
    second_msg: Optional[str] = None
    arrival_code: Optional[int] = None
    arrival_code_name: Optional[str] = None
    is_last_car: bool = False
    transfer_line_ids: list[str] = Field(default_factory=list)
    transfer_station_ids: list[str] = Field(default_factory=list)


class SubwayArrivalResponse(BaseModel):
    fetched_at: datetime
    result_code: str
    result_message: str
    total_count: int
    items: list[SubwayArrivalItem]
    realtime: bool = True
    last_fetched_at: Optional[datetime] = None
