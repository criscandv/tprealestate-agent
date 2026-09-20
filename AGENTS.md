# tprealestate-agent

API de IA (agente) de Top Premium Real Estate (TPRE). Servicio **independiente** en FastAPI +
LangChain/LangGraph que da soporte al CRM (`tprealestate-api`, Django) sin ser parte de él:
chatbot comercial de captación de leads, análisis de imágenes de inmuebles y creación de
contenidos, con OpenAI como LLM principal y Langfuse para observabilidad. Django es la única
fuente de verdad del dominio; el agente lo consulta vía HTTP.

Proyecto de un solo paquete (`app/`), gestionado con **uv**. La documentación operativa vive
en `docs/`.

## When to consult each document

- [`docs/ARCHITECTURE.md`](docs/ARCHITECTURE.md) — stack, estructura de carpetas y convenciones de código.
- [`docs/WORKFLOW.md`](docs/WORKFLOW.md) — cómo trabajamos: planificación (OpenSpec), TDD, verificación, Git.
- [`docs/COMMANDS.md`](docs/COMMANDS.md) — todos los comandos (uv, ruff, pytest, alembic, docker).
- [`docs/ONBOARDING.md`](docs/ONBOARDING.md) — arrancar un clon desde cero.

## Directives

- **Archiving OpenSpec changes:** `/opsx:archive` — or any request to archive, close or finalise a change — is executed by the `spec-archive-agent` subagent (Sonnet): launch it from the repo root with the change name and any decision the user already stated, wait for it, and relay its report; if it returns "decision needed", ask the user and relaunch it. Never run the archive steps inline. Enforced by the `UserPromptSubmit` hook `.claude/hooks/delegate-opsx-archive.sh`.
- **Planificación spec-driven: OpenSpec.** Todo trabajo no trivial pasa por `/opsx:propose` → `/opsx:apply` → `/opsx:archive`. Las propuestas, diseños y tareas viven en `openspec/changes/<id>/`; las specs de larga vida en `openspec/specs/`. No implementar un cambio hasta que sus artefactos estén aprobados. **Nunca** usar `docs/specs/`.
- **Gestor y linter: uv + ruff.** Nada de black/flake8/isort. Formatea y lintea con ruff.
- **Tests: pytest.** Una funcionalidad no está terminada hasta que sus tests están en verde. Se sigue Red-Green-Refactor: el test se escribe antes que la implementación. Ver [`docs/WORKFLOW.md`](docs/WORKFLOW.md#4-tdd) y [`docs/ARCHITECTURE.md`](docs/ARCHITECTURE.md#testing).
- **Quién testea:** al cerrar la fase de preguntas de `/opsx:explore`, `/opsx:propose` o de cualquier plan — y otra vez antes de dar una implementación por terminada — **pregunta al usuario si lo testea él manualmente o lo testeas tú**. Respeta la respuesta durante todo el cambio. Ver [`docs/WORKFLOW.md`](docs/WORKFLOW.md#7-verificación-local).
- **Verificación del servicio:** este proyecto no tiene frontend, así que cuando testeas tú la verificación es contra la API en marcha: levanta el stack (`docker compose up -d`), ejercita el endpoint real en `http://localhost:8040/v1/` y comprueba que aparece en `http://localhost:8040/v1/docs`. Enseña la petición y la respuesta de verdad; un endpoint que solo ha pasado el type-check no está verificado. Ver [`docs/WORKFLOW.md`](docs/WORKFLOW.md#7-verificación-local).
- **Sin redundancia:** antes de escribir código nuevo busca la base, el mixin o el helper que ya existe y hereda o extiende. No copies y pegues lógica entre routers, servicios o nodos del grafo.
- **Ficheros `.env`:** puedes leer el `.env` local mientras esté gitignorado. Nunca copies sus valores a ficheros versionados, commits, PRs, logs ni servicios externos.
- **Push:** cuando el usuario pida push, invoca la skill `gpush`; nunca `git push` directo.
- **Planes:** cuando se pida un plan, no implementar hasta que el usuario lo apruebe.
- **Nunca** commitear a `main` ni usar `--no-verify`.
- **Context7 primero** antes de usar la API de una librería/framework (FastAPI, LangGraph, LangChain, SQLAlchemy, Alembic, OpenAI...).
- **Proyecto hermano `tprealestate-api`:** el CRM en Django del que el agente consume datos. Reutiliza sus convenciones (uv, ruff, estructura por capas) cuando apliquen.
- **Documentación de la API.** Todo endpoint nuevo o modificado tiene que aparecer en el esquema OpenAPI: `response_model`, `summary`, su tag y las respuestas de error que puede devolver. Comprobar que sale en `/v1/docs` antes de dar el trabajo por terminado. Un endpoint que no está en el esquema no está acabado.
- **Comentarios.** Comentar solo lo que el nombre no dice ya. Docstring en clases y funciones cuyo propósito no sea evidente; cualquier otro comentario es **de una sola línea**. Nada de bloques narrativos, ni comentarios repartidos por el fichero, ni repetir lo que hace el código.
