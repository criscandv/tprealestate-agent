from fastapi import APIRouter

api_router = APIRouter()


@api_router.get("/health", tags=["health"])
async def health() -> dict:
    """Comprobacion de vida del servicio."""
    return {"status": "ok"}


# Los routers de cada funcionalidad (chatbot comercial, analisis de imagenes,
# creacion de contenidos) se iran incluyendo aqui durante el desarrollo.
