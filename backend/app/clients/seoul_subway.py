from datetime import datetime, timezone
from typing import Any
import httpx
from app.core.errors import ExternalServiceError, ValidationError
from app.core.settings import settings

ARRIVAL_CODE_MAP = {
    0: "진입",
    1: "도착",
    2: "출발",
    3: "전역출발",
    4: "전역진입",
    5: "전역도착",
    99: "운행중",
}

SUBWAY_LINE_MAP = {
    "1001": "1호선",
    "1002": "2호선",
    "1003": "3호선",
    "1004": "4호선",
    "1005": "5호선",
    "1006": "6호선",
    "1007": "7호선",
    "1008": "8호선",
    "1009": "9호선",
    "1061": "중앙선",
    "1063": "경의중앙선",
    "1065": "공항철도",
    "1067": "경춘선",
    "1075": "수인분당선",
    "1077": "신분당선",
    "1092": "우이신설선",
    "1032": "GTX-A",
}


def parse_ordkey(ordkey: str | None) -> dict:
    if not ordkey:
        return {}
    value = str(ordkey)
    parsed: dict[str, Any] = {
        "ord_updn": value[0] if len(value) >= 1 else None,
        "ord_seq": value[1] if len(value) >= 2 else None,
    }
    if len(value) >= 5:
        try:
            parsed["ord_remaining_stops"] = int(value[2:5])
        except ValueError:
            parsed["ord_remaining_stops"] = None
    if len(value) >= 6:
        parsed["ord_dest_code"] = value[5:-1] if len(value) > 6 else value[5:]
        parsed["ord_express"] = value[-1]
    return parsed


def split_csv(value: Any) -> list[str]:
    if value is None:
        return []
    return [part.strip() for part in str(value).split(",") if part.strip()]


def parse_updn(value: Any) -> int:
    if value in (0, 1, "0", "1"):
        return int(value)
    text = str(value)
    if "하행" in text or "외선" in text:
        return 1
    return 0


def parse_recptn_dt(value: Any) -> datetime:
    if isinstance(value, datetime):
        return value if value.tzinfo else value.replace(tzinfo=timezone.utc)
    text = str(value or "").strip()
    for fmt in ("%Y-%m-%d %H:%M:%S", "%Y%m%d%H%M%S"):
        try:
            return datetime.strptime(text, fmt).replace(tzinfo=timezone.utc)
        except ValueError:
            continue
    return datetime.now(timezone.utc)


class SeoulSubwayClient:
    def __init__(self, client: httpx.AsyncClient | None = None):
        self._own = client is None
        self.client = client or httpx.AsyncClient(timeout=settings.SEOUL_SUBWAY_TIMEOUT_S)

    async def aclose(self) -> None:
        if self._own:
            await self.client.aclose()

    async def get_all(self, start_index: int, end_index: int, response_type: str = "json") -> dict:
        if not settings.SEOUL_SUBWAY_KEY:
            raise ValidationError("Seoul subway API key is not configured")
        if end_index < start_index:
            raise ValidationError("END_INDEX must be greater than or equal to START_INDEX")
        if end_index - start_index + 1 > 1000:
            raise ValidationError("요청은 한 번에 최대 1000건입니다 (ERROR-336)")
        if settings.SEOUL_SUBWAY_KEY == "sample" and end_index > 5:
            raise ValidationError("샘플키는 1~5건만 요청할 수 있습니다 (ERROR-335)")

        base = settings.SEOUL_SUBWAY_BASE_URL.rstrip("/")
        url = (
            f"{base}/{settings.SEOUL_SUBWAY_KEY}/{response_type}"
            f"/realtimeStationArrival/ALL/{start_index}/{end_index}"
        )
        try:
            resp = await self.client.get(url)
        except httpx.HTTPError as exc:
            raise ExternalServiceError("subway request failed", {"reason": str(exc)}) from exc

        try:
            data = resp.json()
        except ValueError as exc:
            raise ExternalServiceError(
                "subway response is not JSON",
                {"http_status": resp.status_code, "body": resp.text[:500]},
            ) from exc

        error = data.get("errorMessage") or data.get("RESULT") or {}
        code = str(error.get("code") or error.get("CODE") or "")
        message = str(error.get("message") or error.get("MESSAGE") or "")
        if code == "INFO-200":
            items = []
            return {
                "url": url,
                "http_status": resp.status_code,
                "content_type": resp.headers.get("content-type"),
                "body": resp.text,
                "json": data,
                "result_code": code,
                "result_message": message or "해당하는 데이터가 없습니다",
                "items": items,
                "record_count": 0,
            }
        if code and not code.startswith("INFO-000"):
            retryable = code in {"ERROR-336", "ERROR-500", "ERROR-600", "ERROR-601"}
            raise ExternalServiceError(
                message or code,
                {"code": code, "retryable": retryable, "http_status": resp.status_code},
            )
        items = data.get("realtimeArrivalList") or []
        return {
            "url": url,
            "http_status": resp.status_code,
            "content_type": resp.headers.get("content-type"),
            "body": resp.text,
            "json": data,
            "result_code": code or "INFO-000",
            "result_message": message or "정상 처리되었습니다",
            "items": items,
            "record_count": len(items),
        }
