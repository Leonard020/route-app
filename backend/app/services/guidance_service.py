from datetime import datetime, timedelta, timezone
from uuid import UUID
from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.errors import NotFoundError, ValidationError
from app.db.session import get_db
from app.domain import messages
from app.domain.geo import haversine_m
from app.domain.timing import remaining_seconds, off_route, should_alert
from app.models.guidance_session import GuidanceSession
from app.models.notification import Notification
from app.models.user_preference import UserPreference
from app.repositories.route_repo import RouteRepository
from app.schemas.guidance import GuidanceOut, GuidanceStartRequest, GuidanceTickRequest
from sqlalchemy import select


class GuidanceService:
    def __init__(self, db: AsyncSession = Depends(get_db)):
        self.db = db
        self.routes = RouteRepository(db)

    async def start(self, payload: GuidanceStartRequest, user=None) -> GuidanceOut:
        if not payload.location_permission:
            raise ValidationError(messages.LOCATION_PERMISSION_REQUIRED)
        route = await self.routes.get_with_steps(payload.route_id)
        if not route:
            raise NotFoundError("route not found")
        steps = [_step_dict(s) for s in route.steps]
        remaining = remaining_seconds(steps, 1)
        loc = payload.current_location
        session = GuidanceSession(
            user_id=user.id if user else None,
            route_id=route.id,
            status="active",
            current_lat=loc.lat if loc else route.origin_lat,
            current_lng=loc.lng if loc else route.origin_lng,
            current_step_order=1,
            remaining_duration_s=remaining,
        )
        self.db.add(session)
        await self.db.commit()
        await self.db.refresh(session)
        alerts = []
        if not payload.notify_permission:
            alerts.append("알림 권한이 없어 화면 내 안내만 제공합니다.")
        return self._out(session, route, alerts=alerts, next_action=steps[0].get("instruction") if steps else None)

    async def tick(self, session_id: str, payload: GuidanceTickRequest, user=None) -> GuidanceOut:
        session = await self._get(session_id)
        route = await self.routes.get_with_steps(session.route_id)
        if not route:
            raise NotFoundError("route not found")
        steps = [_step_dict(s) for s in route.steps]
        step_order = payload.current_step_order or session.current_step_order
        current = next((s for s in route.steps if s.step_order == step_order), None)
        dist = 0.0
        drifted = False
        if current:
            dist = min(
                haversine_m(payload.current_location.lat, payload.current_location.lng, current.start_lat, current.start_lng),
                haversine_m(payload.current_location.lat, payload.current_location.lng, current.end_lat, current.end_lng),
            )
            if current.mode == "walk":
                drifted = off_route(dist, 150)
        remaining = remaining_seconds(steps, step_order)
        transfer_risk = any((s.transit_info or {}).get("transfer_risk") for s in route.steps)
        session.current_lat = payload.current_location.lat
        session.current_lng = payload.current_location.lng
        session.current_step_order = step_order
        session.remaining_duration_s = remaining
        session.off_route = drifted
        session.transfer_risk = transfer_risk
        session.updated_at = datetime.now(timezone.utc)
        if drifted:
            session.status = "off_route"
        alerts = []
        if drifted:
            alerts.append(messages.OFF_ROUTE)
        if transfer_risk:
            alerts.append(messages.TRANSFER_RISK)
        prefs = None
        if user:
            prefs = await self.db.scalar(
                select(UserPreference).where(UserPreference.user_id == user.id)
            )
        minutes = prefs.alert_minutes_before if prefs else 3
        if current and current.mode in ("bus", "subway") and should_alert(int(dist / 8.0) if dist else remaining, minutes):
            title = "하차 안내" if (prefs.alert_alight if prefs else True) else None
            if title and user:
                self.db.add(Notification(
                    user_id=user.id,
                    type="alight",
                    title=title,
                    body=current.instruction,
                    payload={"session_id": str(session.id), "step_order": step_order},
                    channel="in_app" if prefs and not prefs.notify_enabled else "push",
                    status="pending",
                ))
                alerts.append("하차 임박")
        await self.db.commit()
        next_action = current.instruction if current else None
        return self._out(session, route, alerts=alerts, next_action=next_action)

    async def end(self, session_id: str) -> GuidanceOut:
        session = await self._get(session_id)
        route = await self.routes.get_with_steps(session.route_id)
        session.status = "ended"
        session.ended_at = datetime.now(timezone.utc)
        await self.db.commit()
        return self._out(session, route, message="길안내가 종료되었습니다.")

    async def get(self, session_id: str) -> GuidanceOut:
        session = await self._get(session_id)
        route = await self.routes.get_with_steps(session.route_id)
        return self._out(session, route)

    async def _get(self, session_id: str) -> GuidanceSession:
        session = await self.db.get(GuidanceSession, UUID(str(session_id)))
        if not session:
            raise NotFoundError("guidance session not found")
        return session

    def _out(self, session, route, alerts=None, next_action=None, message=None) -> GuidanceOut:
        eta = None
        if route and session.remaining_duration_s:
            eta = datetime.now(timezone.utc) + timedelta(seconds=session.remaining_duration_s)
        return GuidanceOut(
            session_id=str(session.id),
            route_id=str(session.route_id),
            status=session.status,
            current_step_order=session.current_step_order,
            remaining_duration_s=session.remaining_duration_s,
            eta=eta,
            off_route=session.off_route,
            transfer_risk=session.transfer_risk,
            message=message,
            next_action=next_action,
            alerts=alerts or [],
        )


def _step_dict(step) -> dict:
    return {
        "step_order": step.step_order,
        "mode": step.mode,
        "duration_s": step.duration_s,
        "instruction": step.instruction,
        "transit_info": step.transit_info or {},
    }
