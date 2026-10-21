from contextlib import asynccontextmanager
from typing import AsyncGenerator
from fastapi import FastAPI, Request, status
from fastapi.responses import JSONResponse
from app.api.v1.router import api_router
from app.core.config import settings
from app.core.exceptions import EnterpriseRAGException
from app.core.middleware import RequestTracingMiddleware
from app.schemas.errors import ErrorResponse


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None, None]:
    print(f"🚀 Starting up {settings.PROJECT_NAME} in [{settings.ENVIRONMENT}] mode...")
    yield
    print("🛑 Shutting down gracefully...")


def create_application() -> FastAPI:
    application = FastAPI(
        title=settings.PROJECT_NAME,
        version=settings.VERSION,
        lifespan=lifespan,
    )

    application.add_middleware(RequestTracingMiddleware)

    @application.exception_handler(EnterpriseRAGException)
    async def enterprise_rag_exception_handler(
        request: Request, exc: EnterpriseRAGException
    ) -> JSONResponse:
        error_payload = ErrorResponse(
            error_code=exc.error_code,
            message=exc.message,
        )
        return JSONResponse(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            content=error_payload.model_dump(mode="json"),
        )

    application.include_router(api_router, prefix=settings.API_V1_PREFIX)
    return application


app = create_application()
