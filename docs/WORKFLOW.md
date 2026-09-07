# Workflow

Cómo trabajamos en **tprealestate-agent**. Las convenciones de código viven en
[`ARCHITECTURE.md`](./ARCHITECTURE.md); los comandos en [`COMMANDS.md`](./COMMANDS.md). Este
fichero cubre el proceso: dónde vive el contexto, planificación (OpenSpec), TDD, verificación
y Git.

---

## Mapa rápido

```
Brief local        →  specs/<feature>.md         (gitignored, scratch personal)
Cambio (OpenSpec)  →  openspec/changes/<id>/      (versionado, spec-driven)
Rama               →  feat/<feature>
Plan mode          →  Claude diseña + tú apruebas
Implementación     →  ruff formatea al guardar
Quién testea       →  se pregunta al cerrar las preguntas Y antes de dar por hecho
Verificación       →  pytest + ruff + servicio en marcha (localhost:8040/v1/)
Commit             →  pre-commit (ruff + hygiene + pytest)
Push               →  skill gpush
PR / merge         →  gh pr create / gh pr merge --squash --delete-branch
```

---

## 0. Dónde vive el contexto

| Fuente                    | Qué es                                                        | Cuándo leerla                          |
| ------------------------- | ------------------------------------------------------------ | -------------------------------------- |
| `AGENTS.md` / `CLAUDE.md` | Brief raíz y directivas para agentes.                        | Siempre (se cargan cada sesión).       |
| `docs/`                   | Docs operativos (ARCHITECTURE, COMMANDS, este fichero, ONBOARDING). | Cuando la tarea toca ese área.  |
| `specs/`                  | Briefs/planes personales (gitignored salvo `.gitkeep`).      | Por tarea, como brief local.           |
| `openspec/`               | Flujo spec-driven de cambios (ver §5).                       | Para features no triviales y trazables.|

---

## 1. Capturar la intención (brief)

Antes de pedir código, escribe el *qué / por qué* en `specs/<feature>.md` (gitignored). No
necesita estar pulido: su valor es forzarte a aclarar antes de implementar.

```markdown
# <Feature>
## Problema / objetivo
## Entradas / salidas
## Fuera de alcance
## Preguntas abiertas
```

---

## 2. Crear la rama

Nunca se trabaja en `main` (el hook `no-commit-to-branch` lo bloquea).

```bash
git checkout main && git pull
git checkout -b feat/<feature>
```

Prefijos: `feat/`, `fix/`, `chore/`, `refactor/`, `docs/`, `test/`.

---

## 3. Plan mode

Para tareas no triviales, entra en plan mode: Claude lee el brief, explora el código, pregunta
lo ambiguo (`AskUserQuestion`), consulta **Context7** para las librerías implicadas y escribe
el plan. **No implementa hasta que lo apruebas.** Tareas triviales (un typo, una constante)
pueden saltarse el plan.

---

## 4. TDD

La funcionalidad nueva sigue Red → Green → Refactor y **no está terminada hasta que los tests
están en verde**.

1. **Red** — escribe el test que describe el comportamiento y verifica que falla *por la razón
   correcta* (no por un error de sintaxis):
   ```bash
   uv run pytest tests/test_<area>.py::test_<nombre> -vv
   ```
2. **Green** — implementa lo mínimo para pasarlo.
3. **Refactor** — limpia manteniendo los tests verdes.

Qué cubrir en cada área: camino feliz (200/201 con la forma correcta), validación de entrada
(422/400 con las claves de error correctas), casos límite, autorización (401/403) y efectos
(registros creados, llamadas a Django, estado del grafo).

**Excepción:** un bugfix sobre código sin tests previos puede añadir el test junto al arreglo
(test de regresión), siempre que vaya en el mismo PR y el mensaje de commit referencie el bug.

**Stack:** `pytest` + `pytest-asyncio` (`asyncio_mode = "auto"`) + `httpx.AsyncClient` para
ejercitar la app. La configuración vive en `[tool.pytest.ini_options]` de `pyproject.toml` y los
tests en `tests/`, un fichero por área (`test_<area>.py`, funciones `test_<comportamiento>`).

**Convenciones:**

- Patrón AAA (Arrange / Act / Assert), un foco de aserción por test.
- Las llamadas HTTP salientes (Django, OpenAI, Langfuse) se mockean en el borde — nunca se
  golpea un servicio externo real desde la suite.
- Los tests que tocan base de datos usan una transacción que se revierte al terminar.

Comandos en [`COMMANDS.md`](./COMMANDS.md#test).

---

## 5. OpenSpec — cambios spec-driven

Para features no triviales (un módulo nuevo, una capacidad transversal) el proyecto usa
**OpenSpec** para capturar el cambio como artefactos versionados, junto al brief ligero de
`specs/`.

- **Config:** `openspec/config.yaml` (`schema: spec-driven`) lleva el `context` del proyecto
  (stack, convenciones, dominio) que se muestra a la IA al crear artefactos, más `rules` por
  artefacto. Mantenerlo al día según evolucionen las convenciones.
- **Estructura:**
  - `openspec/specs/` — las especificaciones vivas de lo que hace el sistema.
  - `openspec/changes/<id>/` — un cambio en curso (proposal, design, tasks, delta specs).
  - `openspec/changes/archive/` — cambios completados.
- **Skills / comandos:** conduce el flujo con las skills de OpenSpec:
  - `openspec-explore` — pensar una idea (no implementa).
  - `openspec-propose` (`/opsx:propose`) — crear el cambio con todos los artefactos.
  - `openspec-apply-change` (`/opsx:apply`) — implementar sus tareas.
  - `openspec-sync-specs` — plegar los deltas en las specs principales.
  - `openspec-archive-change` (`/opsx:archive`) — finalizar.

**Cuándo usar qué.** Para una tarea rápida y personal, un `specs/<feature>.md` + plan mode
basta. Para un cambio sustancial y trazable (una funcionalidad del PMV: chatbot comercial,
análisis de imágenes, contenidos), prefiere un cambio OpenSpec. Un `specs/` puede sembrar una
propuesta OpenSpec.

> **No usar `docs/specs/`.** La planificación versionada vive en `openspec/`; los briefs
> locales en `specs/`. No crear una carpeta `docs/specs/`.

---

## 6. Context7 antes de tocar una librería

Antes de usar o configurar cualquier framework/librería/SDK (FastAPI, LangGraph, LangChain,
SQLAlchemy, Alembic, OpenAI, Langfuse, Celery...), consulta la documentación actual vía
**Context7** (`mcp__context7__resolve-library-id` → `mcp__context7__query-docs`). No confíes
en la memoria de entrenamiento: las APIs cambian.

---

## 7. Verificación local

Antes del commit, verifica de punta a punta.

### Quién testea

Pregunta al usuario **«¿Quieres testearlo tú o prefieres que lo verifique yo contra la API?»**
en dos momentos:

- Al cerrar la fase de preguntas de `/opsx:explore`, `/opsx:propose` o de cualquier plan.
- Otra vez antes de dar una implementación por terminada, si no se preguntó durante el cambio.

La respuesta decide lo que sigue:

- **Testea Claude** → Claude levanta el stack, ejercita el endpoint real y enseña la petición y
  la respuesta de verdad, además de la suite en verde.
- **Testea el usuario** → Claude igualmente pasa tests, lint y formato, deja el stack levantado y
  entrega las URLs exactas y los pasos para reproducir. No afirma que funciona.

### Comprobaciones automáticas

```bash
uv run ruff check .            # lint limpio
uv run ruff format . --check   # formato consistente
uv run pytest                  # obligatorio antes de dar por hecho
```

### Verificación contra el servicio en marcha

Este proyecto **no tiene frontend**, así que no hay recorrido de navegador: la verificación es
contra la API en marcha. El type-check no es corrección.

```bash
docker compose up -d
curl http://localhost:8040/v1/health        # -> {"status":"ok"}
```

| URL                              | Qué                                  |
| -------------------------------- | ------------------------------------ |
| `http://localhost:8040/v1/`      | La API.                              |
| `http://localhost:8040/v1/docs`  | El esquema OpenAPI.                  |

Ejercita el endpoint que toca el cambio con su payload real y enseña la respuesta. Si el cambio
afecta al grafo del agente, enseña también el estado por el que ha pasado.

### Qué comprobar antes de dar la tarea por terminada

1. La salida del servidor está limpia — sin errores de compilación, tipo o ejecución.
2. El lint está limpio.
3. El formato es consistente (`ruff format --check`).
4. La suite está en verde.
5. El endpoint se ha ejercitado contra el servicio en marcha — o el usuario ha dicho que lo
   testea él, y la entrega lo dice explícitamente.

Si algo falla, arregla la causa antes de entregar. Nunca des por verificado algo que solo ha
pasado el type-check.

---

## 8. Commit

Pre-commit se dispara al hacer `git commit`: formatea y lintea (ruff), aplica hygiene
(whitespace, EOF, YAML/JSON, no commits en `main`) y corre `pytest`. Si un hook modifica
ficheros, el commit falla; re-stage y vuelve a commitear.

```bash
git add .
git commit -m "feat(chatbot): flujo de cualificacion del lead"
```

Mensajes en **Conventional Commits**: `feat:`, `fix:`, `chore:`, `refactor:`, `docs:`,
`test:`, `style:`, `perf:`, `build:`, `ci:`. El cuerpo explica el *porqué*.

---

## 9. Push y PR

- **Push:** cuando el usuario pida push, invoca la skill **`gpush`**; nunca `git push` directo.
- **PR:** `gh pr create` (fallback `mcp__github__*` solo si `gh` no está disponible).
- **Merge:** `gh pr merge <num> --squash --delete-branch`.

---

## Reglas duras — innegociables

1. **Nunca** commitear directamente a `main`; siempre en rama.
2. **Nunca** `--no-verify`; arregla la causa si un hook falla.
3. **Nunca** `git push --force` ni `git reset --hard` sin confirmación explícita.
4. **Context7 primero** antes de proponer la superficie de API de una librería.
5. Para PRs/issues/commits en GitHub, **`gh` primero**; el MCP de GitHub es fallback.
6. Para migraciones **destructivas** (drop de columna/tabla, cambio de tipo, backfill grande),
   pausa y confirma con el usuario.
7. Cuando se pide un plan, **no implementar** hasta que el usuario lo apruebe.
8. **Pregunta quién testea** — al cerrar la fase de preguntas (explore / propose / plan) y otra vez antes de dar el trabajo por terminado.
9. Al pedir push, **invoca `gpush`** — nunca `git push` directo.
10. Gestor y linter: **uv + ruff**. Nada de black/flake8/isort.
