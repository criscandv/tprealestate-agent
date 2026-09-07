# Onboarding

Levantar un clon de **tprealestate-agent** desde cero hasta un servicio en marcha. Comandos
completos en [`COMMANDS.md`](./COMMANDS.md).

---

## Prerrequisitos

- **Python 3.12** (ver `.python-version`).
- **uv** — gestor de paquetes/entornos. Instalación: `curl -LsSf https://astral.sh/uv/install.sh | sh`.
- **Docker** + **Docker Compose** (para el modo contenedores).
- Acceso a: una clave de **OpenAI**, un proyecto de **Langfuse** (ya desplegado) y la **API de
  Django** (`tprealestate-api`) en marcha si se van a usar las tools contra el CRM.

---

## Variables de entorno

```bash
cp .env.example .env
```

Rellena en `.env`:

- `OPENAI_API_KEY` — clave de OpenAI.
- `LANGFUSE_PUBLIC_KEY` / `LANGFUSE_SECRET_KEY` / `LANGFUSE_HOST` — del proyecto Langfuse.
- `DJANGO_API_BASE_URL` — URL de la API de Django (p. ej. `http://host.docker.internal:8030/v1`).
- `DJANGO_JWT_SECRET` — el `SECRET_KEY` con el que Django firma sus JWT (para verificarlos).
- `SERVICE_API_KEY` — API key de servicio que aceptará el agente en la cabecera `X-API-Key`.
- `DJANGO_SERVICE_API_KEY` — API key que el agente enviará a Django (acciones anónimas/sistema).
- `POSTGRES_*` / `DATABASE_URL` — base de datos propia del agente (ya vienen con defaults).

> Los defaults de `POSTGRES_*` y `REDIS_URL` apuntan a los servicios del `docker-compose`.

---

## Arranque (Docker) — recomendado

```bash
docker compose up --build
```

Levanta la API + PostgreSQL(pgvector) + Redis. La API queda en
`http://localhost:8040/v1/docs`.

---

## Arranque (nativo)

```bash
uv sync                                   # instala dependencias
uv run pre-commit install                 # hooks de git
# necesitas un PostgreSQL y un Redis accesibles (ajusta DATABASE_URL / REDIS_URL en .env)
uv run alembic upgrade head               # aplica migraciones (cuando existan modelos)
uv run uvicorn app.main:app --reload      # http://localhost:8000/v1/docs
```

---

## Verificar que funciona

```bash
curl http://localhost:8000/v1/health      # nativo  -> {"status":"ok"}
curl http://localhost:8040/v1/health      # docker  -> {"status":"ok"}
uv run pytest                             # la suite (incluye el smoke de health) en verde
```

---

## Problemas comunes

- **`uv sync` falla resolviendo dependencias de LangChain/LangGraph.** Ejecuta `uv lock` para
  regenerar el lockfile y vuelve a `uv sync`.
- **La API responde 401 en todo salvo `/v1/health` y `/v1/docs`.** Es esperado: el middleware
  exige la cabecera `X-API-Key` (placeholder de la Fase 0). Envía cualquier valor no vacío
  mientras la auth real está en desarrollo.
- **El agente no llega a Django desde Docker.** Usa `host.docker.internal` en
  `DJANGO_API_BASE_URL` (ya configurado en `.env.example`).
- **Puerto 8000 ocupado.** En Docker la API se publica en el **8040**, su hueco en el reparto
  del workspace (`../../../devtools/docs/PUERTOS.md`), para no chocar con las cuatro APIs Django locales.
