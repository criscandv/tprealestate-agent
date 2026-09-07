# Commands

Referencia de comandos de **tprealestate-agent**, agrupados por tarea. Convenciones y proceso
en [`WORKFLOW.md`](./WORKFLOW.md); arranque desde cero en [`ONBOARDING.md`](./ONBOARDING.md).

Gestión de paquetes y ejecución: **uv**. Lint/format: **ruff**. Tests: **pytest**.

---

## Setup

```bash
cp .env.example .env          # completar OpenAI, Langfuse, Django, secretos
uv sync                       # crear el entorno e instalar dependencias (incl. dev)
uv run pre-commit install     # activar los hooks de pre-commit
```

## Run (nativo)

```bash
uv run uvicorn app.main:app --reload            # dev con recarga (http://localhost:8000)
uv run uvicorn app.main:app --host 0.0.0.0 --port 8000   # sin recarga
```

Docs interactivas: `http://localhost:8000/v1/docs` (o `:8040` con Docker, ver abajo).

## Run (Docker)

```bash
docker compose up --build        # levanta api + PostgreSQL(pgvector) + Redis
docker compose up -d              # en segundo plano
docker compose logs -f tprealestate-agent-api
docker compose down               # parar (conserva el volumen de datos)
docker compose down -v            # parar y borrar el volumen de la BD
```

La API queda en `http://localhost:8040/v1/docs` (mismo puerto dentro y fuera del
contenedor; ver el reparto del workspace en `../../../devtools/docs/PUERTOS.md`).

## Dependencias (uv)

```bash
uv add <paquete>                  # añadir dependencia de runtime
uv add --dev <paquete>            # añadir dependencia de desarrollo
uv remove <paquete>               # quitar
uv lock                           # regenerar el lockfile
uv sync                           # sincronizar el entorno con el lock
```

## Test

```bash
uv run pytest                     # toda la suite
uv run pytest -vv                 # detallado
uv run pytest tests/test_health.py::test_health_ok -vv   # un test
```

## Lint / Format

```bash
uv run ruff check .               # lint
uv run ruff check . --fix         # lint con autofix
uv run ruff format .              # formatear
uv run ruff format . --check      # comprobar formato sin escribir
uv run pre-commit run --all-files # todos los hooks sobre todo el repo
```

## Base de datos (Alembic)

```bash
uv run alembic revision --autogenerate -m "descripcion"   # crear migración
uv run alembic upgrade head                                # aplicar
uv run alembic downgrade -1                                # revertir la última
uv run alembic history                                     # historial
```

> Para el autogenerate, importa el modelo nuevo en `alembic/env.py`.

## Verificación rápida

```bash
curl http://localhost:8000/v1/health      # -> {"status":"ok"}
```
