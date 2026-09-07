import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import RedirectResponse

from app.api.router import api_router
from app.core.config import settings
from app.middlewares.api_key_middleware import APIKeyMiddleware
from app.middlewares.proxy_headers_middleware import ProxyHeadersMiddleware

logging.basicConfig(
    level=settings.LOG_LEVEL,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[logging.StreamHandler(), logging.FileHandler(f"{settings.LOG_DIR}/app.log")],
)

logger = logging.getLogger(__name__)

cors_origins = ["*"]


@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("Starting up TPRE Agent...")
    yield
    logger.info("Shutting down TPRE Agent...")


def create_main_application() -> FastAPI:
    """Aplicacion principal del servicio de IA."""
    application = FastAPI(
        title=settings.APP_NAME,
        description=settings.APP_DESCRIPTION,
        version=settings.APP_VERSION,
        openapi_url=f"{settings.API_PREFIX}/openapi.json",
        docs_url=f"{settings.API_PREFIX}/docs",
        redoc_url=f"{settings.API_PREFIX}/redoc",
        lifespan=lifespan,
    )

    application.add_middleware(
        CORSMiddleware,
        allow_origins=cors_origins,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    # Rutas que no exigen autenticacion (docs y health).
    excluded_paths = [
        "/v1/health",
        "/v1/docs",
        "/v1/redoc",
        "/v1/openapi.json",
    ]

    application.add_middleware(ProxyHeadersMiddleware)
    application.add_middleware(APIKeyMiddleware, excluded_paths=excluded_paths)

    @application.get("/")
    async def redirect_to_docs():
        return RedirectResponse(url="/v1/docs")

    application.include_router(api_router, prefix="/v1")

    return application


app = create_main_application()
