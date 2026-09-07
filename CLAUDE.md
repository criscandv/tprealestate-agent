# tprealestate-agent — Claude

Las instrucciones de este repo viven en [`AGENTS.md`](AGENTS.md). Léelo primero.

## Directivas específicas de Claude

- Planificación spec-driven con **OpenSpec** (`/opsx:propose` → `/opsx:apply` → `/opsx:archive`). No implementar hasta que el plan/artefactos estén aprobados. Nunca usar `docs/specs/`.
- Para push, invoca la skill **`gpush`** — nunca `git push` directo.
- Gestor/linter: **uv + ruff** (no black/flake8/isort). Tests con **pytest**.
- Antes de usar la API de una librería, **Context7 primero**.
- Skills útiles en este proyecto: `fastapi`, `langgraph-cli`, `langgraph-persistence`, `langgraph-human-in-the-loop`, `langchain-rag`, `building-pydantic-ai-agents`, `python-tooling`, `openspec-*`.
