import logging

from fastapi import FastAPI, Request, status
from fastapi.encoders import jsonable_encoder
from fastapi.responses import JSONResponse

from core.shared.errors import (
    ConflictingParametersError,
    InvalidParametersError,
    ResourceNotFoundError,
)


def _extract_message(exc: Exception) -> str:
    if hasattr(exc, "message"):
        return exc.message

    if hasattr(exc, "detail"):
        return exc.detail

    if hasattr(exc, "args") and len(exc.args) > 0:
        return exc.args[0]

    return ""


def inject_exception_handlers(app: FastAPI):
    @app.exception_handler(ConflictingParametersError)
    async def status_409_exception_handler(
        request: Request, exc: ConflictingParametersError
    ):
        message = _extract_message(exc)
        return JSONResponse(
            status_code=status.HTTP_409_CONFLICT,
            content=jsonable_encoder({"message": message}),
        )

    @app.exception_handler(ResourceNotFoundError)
    async def status_404_exception_handler(
        request: Request, exc: ResourceNotFoundError
    ):
        message = _extract_message(exc)
        return JSONResponse(
            status_code=status.HTTP_404_NOT_FOUND,
            content=jsonable_encoder({"message": message}),
        )

    @app.exception_handler(InvalidParametersError)
    async def status_422_exception_handler(
        request: Request, exc: InvalidParametersError
    ):
        message = _extract_message(exc)
        return JSONResponse(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            content=jsonable_encoder({"message": message}),
        )

    @app.exception_handler(Exception)
    async def status_500_exception_handler(request: Request, exc: Exception):
        base_error_message = f"Failed to execute: {request.method}: {request.url}"
        logging.error("Unexpected error: %s. Detail: %s", base_error_message, exc)

        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content=jsonable_encoder({"message": str(exc)}),
        )
