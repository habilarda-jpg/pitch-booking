from fastapi import FastAPI, Request, status
from fastapi.responses import JSONResponse

from pitch_booking.api.routes import router
from pitch_booking.bootstrap import Container, build_container
from pitch_booking.domain.errors import (
    DomainError,
    InvalidStateTransitionError,
    NotFoundError,
    PaymentDeclinedError,
    PermissionDeniedError,
    SlotUnavailableError,
)

STATUS_BY_ERROR: dict[type[DomainError], int] = {
    NotFoundError: status.HTTP_404_NOT_FOUND,
    SlotUnavailableError: status.HTTP_409_CONFLICT,
    InvalidStateTransitionError: status.HTTP_409_CONFLICT,
    PaymentDeclinedError: status.HTTP_402_PAYMENT_REQUIRED,
    PermissionDeniedError: status.HTTP_403_FORBIDDEN,
}


def create_app(container: Container | None = None) -> FastAPI:
    app = FastAPI(title="Pitch Booking API", version="0.1.0")
    app.state.container = container or build_container(seed=True)
    app.include_router(router)

    @app.exception_handler(DomainError)
    def handle_domain_error(request: Request, exc: DomainError) -> JSONResponse:
        code = STATUS_BY_ERROR.get(type(exc), status.HTTP_400_BAD_REQUEST)
        return JSONResponse(status_code=code, content={"detail": str(exc)})

    return app


app = create_app()
