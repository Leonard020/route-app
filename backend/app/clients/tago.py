from typing import Any
import httpx
from app.core.errors import ExternalServiceError, ValidationError
from app.core.settings import settings

PORTAL_ERRORS = {
    "1": "APPLICATION_ERROR",
    "4": "HTTP_ERROR",
    "12": "NO_OPENAPI_SERVICE_ERROR",
    "20": "SERVICE_ACCESS_DENIED_ERROR",
    "22": "LIMITED_NUMBER_OF_SERVICE_REQUESTS_EXCEEDS_ERROR",
    "30": "SERVICE_KEY_IS_NOT_REGISTERED_ERROR",
    "31": "DEADLINE_HAS_EXPIRED_ERROR",
    "32": "UNREGISTERED_IP_ERROR",
    "99": "UNKNOWN_ERROR",
}


def _as_list(items: Any) -> list[dict]:
    if items is None:
        return []
    if isinstance(items, list):
        return items
    if isinstance(items, dict):
        inner = items.get("item", items)
        if isinstance(inner, list):
            return inner
        if isinstance(inner, dict):
            return [inner]
    return []


class TagoClient:
    def __init__(self, client: httpx.AsyncClient | None = None):
        self._own = client is None
        self.client = client or httpx.AsyncClient(timeout=settings.TAGO_TIMEOUT_S)

    async def aclose(self) -> None:
        if self._own:
            await self.client.aclose()

    async def _get(self, path: str, params: dict) -> dict:
        if not settings.TAGO_SERVICE_KEY:
            raise ValidationError("TAGO serviceKey is not configured")
        query = {
            "serviceKey": settings.TAGO_SERVICE_KEY,
            "_type": "json",
            **{k: v for k, v in params.items() if v is not None},
        }
        url = f"{settings.TAGO_BASE_URL.rstrip('/')}/{path}"
        try:
            resp = await self.client.get(url, params=query)
        except httpx.HTTPError as exc:
            raise ExternalServiceError("TAGO request failed", {"reason": str(exc)}) from exc

        content_type = resp.headers.get("content-type", "")
        body_text = resp.text
        if "xml" in content_type.lower() or body_text.lstrip().startswith("<"):
            self._raise_portal_xml(body_text, resp.status_code)

        try:
            data = resp.json()
        except ValueError as exc:
            raise ExternalServiceError(
                "TAGO response is not JSON",
                {"http_status": resp.status_code, "body": body_text[:500]},
            ) from exc

        header = ((data.get("response") or {}).get("header") or {})
        result_code = str(header.get("resultCode") or "")
        result_msg = str(header.get("resultMsg") or "")
        if result_code and result_code not in ("00", "0"):
            if result_code == "99":
                message = "INVALID_REQUEST_PARAMETER_ERROR"
            else:
                message = result_msg or PORTAL_ERRORS.get(result_code, "TAGO error")
            raise ExternalServiceError(
                message,
                {"resultCode": result_code, "resultMsg": result_msg},
            )
        return {
            "url": str(resp.url),
            "http_status": resp.status_code,
            "content_type": content_type,
            "body": body_text,
            "json": data,
            "result_code": result_code or "00",
            "result_msg": result_msg or "NORMAL SERVICE",
        }

    def _raise_portal_xml(self, body: str, status: int) -> None:
        code = ""
        msg = "TAGO XML error"
        if "<returnReasonCode>" in body:
            code = body.split("<returnReasonCode>")[1].split("</returnReasonCode>")[0]
        if "<returnAuthMsg>" in body:
            msg = body.split("<returnAuthMsg>")[1].split("</returnAuthMsg>")[0]
        raise ExternalServiceError(
            PORTAL_ERRORS.get(code, msg),
            {"returnReasonCode": code, "http_status": status},
        )

    async def get_city_codes(self) -> dict:
        raw = await self._get("getCtyCodeList", {})
        items = _as_list(((raw["json"].get("response") or {}).get("body") or {}).get("items"))
        return {**raw, "items": items, "total_count": len(items)}

    async def get_stop_arrivals(
        self,
        *,
        city_code: str,
        node_id: str,
        num_of_rows: int = 10,
        page_no: int = 1,
    ) -> dict:
        raw = await self._get(
            "getSttnAcctoArvlPrearngeInfoList",
            {
                "cityCode": city_code,
                "nodeId": node_id,
                "numOfRows": num_of_rows,
                "pageNo": page_no,
            },
        )
        body = (raw["json"].get("response") or {}).get("body") or {}
        items = _as_list(body.get("items"))
        return {
            **raw,
            "items": items,
            "num_of_rows": body.get("numOfRows"),
            "page_no": body.get("pageNo"),
            "total_count": body.get("totalCount", len(items)),
        }

    async def get_route_arrivals(
        self,
        *,
        city_code: str,
        node_id: str,
        route_id: str,
        num_of_rows: int = 10,
        page_no: int = 1,
    ) -> dict:
        raw = await self._get(
            "getSttnAcctoSpcifyRouteBusArvlPrearngeInfoList",
            {
                "cityCode": city_code,
                "nodeId": node_id,
                "routeId": route_id,
                "numOfRows": num_of_rows,
                "pageNo": page_no,
            },
        )
        body = (raw["json"].get("response") or {}).get("body") or {}
        items = _as_list(body.get("items"))
        return {
            **raw,
            "items": items,
            "num_of_rows": body.get("numOfRows"),
            "page_no": body.get("pageNo"),
            "total_count": body.get("totalCount", len(items)),
        }
