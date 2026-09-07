# Architecture

Cómo encajan las piezas de **tprealestate-agent**, dónde vive cada responsabilidad y qué
convenciones de código seguimos. Los comandos viven en [`COMMANDS.md`](./COMMANDS.md); el
proceso de trabajo en [`WORKFLOW.md`](./WORKFLOW.md).

---

## Propósito

Servicio de IA (agente) de Top Premium Real Estate. API **independiente** en FastAPI +
LangChain/LangGraph que da soporte al CRM inmobiliario (Django `tprealestate-api`) sin ser
parte de él. Django es la **única fuente de verdad** del dominio; el agente consulta y
escribe contra su API.

---

## Visión de sistema

```
Canales (widget web, backoffice, WhatsApp/RRSS en el futuro)
        │  HTTP (JWT de usuario  |  X-API-Key de servicio)
        ▼
┌─────────────────────────────────────────────────────────┐
│  tprealestate-agent  (FastAPI, async)                    │
│                                                          │
│   API (app/api)  →  Grafos LangGraph (app/services/llm)  │
│        │                     │                           │
│        │              ┌──────┴───────┬─────────────┐     │
│        ▼              ▼              ▼             ▼      │
│   Middlewares   Tools (httpx →   RAG (pgvector) Monitoring│
│   (auth)         Django CRM)                    (Langfuse)│
│        │                                                 │
│        ▼                                                 │
│   PostgreSQL propio (estado del agente + checkpointer)   │
│   Redis + Celery (tareas en segundo plano)               │
└─────────────────────────────────────────────────────────┘
        │  HTTP (cliente tipado)
        ▼
   Django REST API (CRM: leads, inmuebles, agenda, zonas)
```

El agente **no** comparte base de datos con Django: tiene su propio PostgreSQL para el estado
conversacional y el checkpointer de LangGraph. Toda lectura/escritura del dominio pasa por la
API de Django.

---

## Estructura del repositorio

```
tprealestate-agent/
├── app/
│   ├── main.py               # arranque FastAPI (middlewares, CORS, router, lifespan)
│   ├── core/
│   │   ├── config.py         # settings (pydantic-settings): DB, OpenAI, Langfuse, Django, Redis
│   │   └── security.py       # helpers (generación de API keys, uuids, expiración)
│   ├── api/
│   │   ├── router.py         # api_router raíz (incluye /v1/health y los routers por feature)
│   │   ├── deps.py           # dependencias compartidas (auth, get_db)
│   │   └── v1/endpoints/     # endpoints por funcionalidad (se irán añadiendo)
│   ├── db/
│   │   ├── base.py           # Base declarativa + BaseModel (id UUID, timestamps, is_active)
│   │   └── models/           # modelos SQLAlchemy del agente
│   ├── services/
│   │   ├── database.py       # engine + SessionLocal + get_db
│   │   ├── llm/
│   │   │   ├── agent/        # grafos LangGraph (chatbot comercial, etc.)
│   │   │   ├── prompts/      # prompts del sistema y por flujo
│   │   │   └── tools/        # tools del agente (cliente httpx → Django)
│   │   ├── rag/              # ingestión y recuperación (pgvector) — fases posteriores
│   │   └── monitoring/
│   │       └── langfuse.py   # cliente Langfuse (observabilidad)
│   ├── schemas/              # modelos Pydantic de entrada/salida
│   └── middlewares/
│       ├── api_key_middleware.py     # exige X-API-Key (placeholder; auth real en desarrollo)
│       └── proxy_headers_middleware.py
├── alembic/                  # migraciones (env.py apunta a app.db.base.Base)
├── tests/                    # pytest (smoke test de /v1/health incluido)
├── docs/                     # esta documentación operativa
├── openspec/                 # flujo spec-driven (ver WORKFLOW.md §Planificación)
├── docker-compose.yml        # api + PostgreSQL(pgvector) + Redis
├── Dockerfile                # imagen basada en uv
└── pyproject.toml            # dependencias y config de ruff/pytest (gestión con uv)
```

---

## Stack por pieza

| Pieza                | Tecnología                                              |
| -------------------- | ------------------------------------------------------- |
| API / web framework  | FastAPI (async) + Uvicorn                               |
| Lenguaje / tooling   | Python 3.12, gestionado con **uv**; lint/format **ruff**|
| Orquestación de IA   | LangGraph (flujos con estado) + LangChain               |
| LLM                  | OpenAI (GPT-4o) principal, capa abstraída (swappable)   |
| Persistencia         | PostgreSQL + pgvector (propio del agente); SQLAlchemy 2 |
| Migraciones          | Alembic                                                 |
| Tareas asíncronas    | Redis + Celery                                          |
| Observabilidad       | Langfuse                                                |
| Integración CRM      | Cliente httpx tipado contra la API de Django            |

---

## Fronteras de responsabilidad

- **`app/api`** — expone endpoints, valida entrada/salida (schemas) y delega en servicios. No
  contiene lógica de negocio pesada.
- **`app/services/llm`** — el "cerebro": grafos LangGraph, prompts y tools. Aquí vive la lógica
  conversacional del chatbot comercial y demás flujos.
- **`app/services/llm/tools`** — el único lugar que habla con Django (vía cliente httpx). El
  resto del código no llama a Django directamente.
- **`app/db`** — estado propio del agente (conversaciones, checkpoints). No modela el dominio
  del CRM (eso vive en Django).
- **`app/middlewares`** — autenticación de entrada y cabeceras de proxy.
- **Django (`tprealestate-api`)** — fuente de verdad del dominio (leads, inmuebles, agenda,
  zonas). El agente nunca escribe en su base de datos directamente.

---

## Autenticación (modelo híbrido)

- **Usuario identificado** (backoffice, franquiciado, cliente logueado): el frontend envía el
  **JWT de Django**; el agente lo verifica y lo **reenvía** al CRM, que devuelve los datos de
  ese usuario aplicando sus permisos.
- **Visitante anónimo** (chatbot web) y **tareas de sistema** (seguimientos, análisis de
  imágenes): sin JWT → el agente usa una **API key de servicio** para acciones acotadas.

En el estado actual (Fase 0) el middleware solo exige la cabecera `X-API-Key` como
*placeholder*; la verificación real (firma del JWT + validación de la key de servicio) se
implementa durante el desarrollo.

---

## Convenciones de código

- **Idioma:** identificadores, nombres de fichero y código en **inglés**; textos de cara al
  usuario (prompts, respuestas al lead) en **castellano**.
- **Estilo:** ruff como linter y formatter (línea 120, comillas dobles). Sin black/flake8/isort.
- **Tipado:** anotaciones de tipos en funciones públicas y firmas de servicios/tools.
- **Estructura por capas** bajo `app/`: la lógica no vive en los endpoints, sino en `services/`.
- **Config por entorno:** todo lo configurable pasa por `app/core/config.py` (nada de valores
  mágicos incrustados).
- **Tests:** pytest; una funcionalidad no está terminada hasta que sus tests están en verde
  (ver [`WORKFLOW.md`](./WORKFLOW.md)).

---

## Testing

TDD obligatorio: cada endpoint, servicio, tool o nodo del grafo nuevo llega junto a su test,
escrito antes. El bucle Red-Green-Refactor está en [`WORKFLOW.md`](./WORKFLOW.md#4-tdd).

Los tests viven en `tests/`, un fichero por área:

```
tests/
  conftest.py            # fixtures compartidas (cliente async, settings de test, mocks de borde)
  test_health.py         # el endpoint de salud
  test_<area>.py         # endpoints, servicios y nodos del grafo por área
```

**Stack:** `pytest` + `pytest-asyncio` (`asyncio_mode = "auto"`) + `httpx.AsyncClient` contra la
app. La configuración vive en `[tool.pytest.ini_options]` de `pyproject.toml`.

**Convenciones:**

- Nombres: ficheros `test_*.py`, funciones `test_<comportamiento>` (frase completa con guiones bajos).
- Patrón AAA (Arrange / Act / Assert), un foco de aserción por test.
- Nunca se golpea un servicio externo real (Django, OpenAI, Langfuse): se mockean en el borde,
  en la capa de cliente HTTP, no dentro de la lógica de negocio.
- Cubre siempre: camino feliz, validación de entrada (422/400), autorización (401/403) y los
  efectos observables (registros creados, llamadas salientes, estado del grafo).
- Los tests que tocan base de datos corren dentro de una transacción que se revierte.

**Objetivo de cobertura:** 80% mínimo sobre `app/`. Ejecuta la suite con
`uv run pytest --cov=app --cov-report=term-missing`.

Comandos completos en [`COMMANDS.md`](./COMMANDS.md#test).

---

## Log de decisiones

- **Servicio separado de Django (no un app de Django).** Runtime async, streaming y estado
  conversacional tienen necesidades distintas; separarlo permite escalar y desplegar aparte.
- **Base de datos propia del agente.** Mantiene nítido el límite: el CRM no se contamina con
  tablas de estado del agente y viceversa.
- **Tools HTTP contra Django, "MCP-ready".** Más simple que un MCP para el PMV; el diseño
  permite exponerlas como servidor MCP en el futuro sin reescribir.
- **OpenAI principal, capa abstraída.** GPT-4o por su tooling multimodal y function-calling;
  la abstracción deja cambiar a Gemini sin tocar los flujos.
- **uv + ruff.** Alineado con `tprealestate-api` para homogeneizar el monorepo de proyectos.
