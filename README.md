# tprealestate-agent

API de IA (agente) de Top Premium Real Estate. FastAPI + LangChain/LangGraph,
gestionada con uv. Servicio independiente que apoya al CRM (Django). Consulta
`AGENTS.md` para la guia de desarrollo.

## Arranque rapido

    cp .env.example .env   # completa las claves (OpenAI, Langfuse, Django...)
    uv sync
    uv run uvicorn app.main:app --reload

    # o con Docker (api + PostgreSQL + Redis):
    docker compose up --build

Documentacion interactiva: http://localhost:8040/v1/docs
