from fastapi import Request, FastAPI
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from starlette.exceptions import HTTPException as StarletteHTTPException


class AppError(Exception):
    code = "SERVER_500"
    status = 500
    message = "internal error"

    def __init__(self, message: str | None = None, details: dict | None = None):
        self.message = message or self.message
        self.details = details or {}


class AuthError(AppError):
    code = "AUTH_401"
    status = 401
    message = "unauthorized"


class ForbiddenError(AppError):
    code = "AUTH_403"
    status = 403
    message = "forbidden"


class NotFoundError(AppError):
    code = "NOT_FOUND_404"
    status = 404
    message = "not found"


class ValidationError(AppError):
    code = "VALID_400"
    status = 400
    message = "invalid request"


class RateLimitError(AppError):
    code = "RATE_429"
    status = 429
    message = "too many requests"


class ExternalServiceError(AppError):
    code = "EXTERNAL_502"
    status = 502
    message = "upstream error"


def _envelope(code: str, message: str, details: dict | None = None) -> dict:
    return {
        "success": False,
        "data": None,
        "error": {"code": code, "message": message, "details": details or {}},
    }


def register_exception_handlers(app: FastAPI) -> None:
    @app.exception_handler(AppError)
    async def _app_error(_: Request, exc: AppError):
        return JSONResponse(
            status_code=exc.status,
            content=_envelope(exc.code, exc.message, exc.details),
        )

    @app.exception_handler(RequestValidationError)
    async def _validation(_: Request, exc: RequestValidationError):
        return JSONResponse(
            status_code=400,
            content=_envelope("VALID_400", "invalid request", {"errors": exc.errors()}),
        )

    @app.exception_handler(StarletteHTTPException)
    async def _http(_: Request, exc: StarletteHTTPException):
        code = {401: "AUTH_401", 403: "AUTH_403", 404: "NOT_FOUND_404",
                429: "RATE_429"}.get(exc.status_code, "SERVER_500")
        return JSONResponse(
            status_code=exc.status_code,
            content=_envelope(code, str(exc.detail)),
        )

    @app.exception_handler(Exception)
    async def _unhandled(_: Request, exc: Exception):
        return JSONResponse(
            status_code=500,
            content=_envelope("SERVER_500", "internal error"),
        )