from fastapi import APIRouter, Depends, Query
from app.core.response import Envelope
from app.schemas.transit import SubwayArrivalResponse
from app.services.subway_service import SubwayService

router = APIRouter()


@router.get("/lines")
async def lines(svc: SubwayService = Depends()):
    return Envelope(data=await svc.list_lines())


@router.get("/arrivals", response_model=Envelope[SubwayArrivalResponse])
async def arrivals(
    stationName: str | None = Query(None, description="지하철역명"),
    subwayId: str | None = Query(None, description="지하철호선ID (1001~1032)"),
    stationId: str | None = Query(None, description="지하철역ID"),
    updnLine: int | None = Query(None, ge=0, le=1),
    startIndex: int = Query(1, ge=1),
    endIndex: int | None = Query(None),
    svc: SubwayService = Depends(),
):
    data = await svc.arrivals(
        station_name=stationName,
        subway_id=subwayId,
        station_id=stationId,
        updn_line=updnLine,
        start_index=startIndex,
        end_index=endIndex,
    )
    return Envelope(data=data)


@router.post("/sync")
async def sync_all(svc: SubwayService = Depends()):
    data = await svc.sync_all()
    return Envelope(data=data)
