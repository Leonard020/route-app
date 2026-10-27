from fastapi import APIRouter, Depends, Query
from app.core.response import Envelope
from app.schemas.transit import BusArrivalResponse, CityCodeItem
from app.services.bus_service import BusService

router = APIRouter()


@router.get("/cities", response_model=Envelope[list[CityCodeItem]])
async def city_codes(
    refresh: bool = Query(False),
    svc: BusService = Depends(),
):
    data = await svc.list_cities(refresh=refresh)
    return Envelope(data=data)


@router.get("/arrivals", response_model=Envelope[BusArrivalResponse])
async def stop_arrivals(
    cityCode: str = Query(..., description="도시코드 (getCtyCodeList)"),
    nodeId: str = Query(..., description="정류소ID"),
    numOfRows: int = Query(10, ge=1, le=100),
    pageNo: int = Query(1, ge=1),
    svc: BusService = Depends(),
):
    data = await svc.arrivals(
        city_code=cityCode, node_id=nodeId, num_of_rows=numOfRows, page_no=pageNo
    )
    return Envelope(data=data)


@router.get("/arrivals/route", response_model=Envelope[BusArrivalResponse])
async def route_arrivals(
    cityCode: str = Query(...),
    nodeId: str = Query(...),
    routeId: str = Query(..., description="노선ID"),
    numOfRows: int = Query(10, ge=1, le=100),
    pageNo: int = Query(1, ge=1),
    svc: BusService = Depends(),
):
    data = await svc.arrivals(
        city_code=cityCode,
        node_id=nodeId,
        route_id=routeId,
        num_of_rows=numOfRows,
        page_no=pageNo,
    )
    return Envelope(data=data)
