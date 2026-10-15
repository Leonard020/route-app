from typing import Generic, TypeVar, Optional, Any
from pydantic import BaseModel

T = TypeVar("T")


class ErrorInfo(BaseModel):
    code: str
    message: str
    details: Optional[dict[str, Any]] = None


class Meta(BaseModel):
    request_id: Optional[str] = None
    timestamp: Optional[str] = None
    predictor_fallback: Optional[bool] = None
    predictor_version: Optional[str] = None


class Envelope(BaseModel, Generic[T]):
    success: bool = True
    data: Optional[T] = None
    error: Optional[ErrorInfo] = None
    meta: Optional[Meta] = None


def ok(data: Any = None, meta: Meta | None = None) -> dict:
    return {"success": True, "data": data, "error": None, "meta": meta}