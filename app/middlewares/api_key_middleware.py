import json
import logging
from typing import Callable, List, Optional

from fastapi import FastAPI, Request, Response
from starlette.middleware.base import BaseHTTPMiddleware

logger = logging.getLogger(__name__)


class APIKeyMiddleware(BaseHTTPMiddleware):
    """Exige la cabecera X-API-Key en todas las rutas salvo las excluidas.

    Placeholder de la Fase 0: solo comprueba la presencia de la cabecera. La
    autenticacion real (JWT de usuario reenviado o API key de servicio validada)
    se implementa mas adelante.
    """

    def __init__(self, app: FastAPI, excluded_paths: Optional[List[str]] = None):
        super().__init__(app)
        self.excluded_paths = excluded_paths or []
        logger.info("Rutas excluidas de la verificacion de API Key: %s", self.excluded_paths)

    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        path = request.url.path

        if request.method == "OPTIONS":
            return await call_next(request)

        for excluded_path in self.excluded_paths:
            if path.endswith(excluded_path):
                return await call_next(request)

        api_key = request.headers.get("X-API-Key")
        if not api_key:
            return Response(
                content=json.dumps({"detail": "API Key is required"}),
                status_code=401,
                headers={"WWW-Authenticate": "X-API-Key", "Content-Type": "application/json"},
            )

        return await call_next(request)
