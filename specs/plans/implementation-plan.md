# reflex-pragmatic-drag-and-drop — Implementation Plan

## Metadata

| Campo | Valor |
|---|---|
| **Autor** | Ernesto (ecrespo) |
| **Estado** | `IN_PROGRESS` |
| **Versión** | 1.0 |
| **Fecha** | 2026-06-14 |
| **PRD** | ../prd/reflex-pragmatic-dnd.md |
| **Tech Design** | ../technical/architecture.md |
| **Data Model** | ../data-model/event-payloads.md |
| **API Spec** | ../api/component-api-v1.md |

---

## 1. Resumen de Implementación

Construcción incremental en 5 fases, de la base del proyecto al empaquetado para
PyPI. El núcleo (Fases 1-3) ya está implementado en este repositorio; las Fases 4-5
quedan como trabajo planificado. Enfoque: envolver primero el core, validar con un
ejemplo real (Kanban), luego añadir hitbox/auto-scroll y, por último, pulido y
publicación.

**Duración estimada total:** ~3 sprints (1 dev).
**Fecha objetivo v1.0:** por definir.

## 2. Pre-requisitos

| Pre-requisito | Owner | Estado | Notas |
|---|---|---|---|
| Specs aprobados (PRD/API/Tech/Data) | Ernesto | ☑ Borrador listo | Este directorio `specs/`. |
| Toolchain: `uv`, Python 3.12, Reflex 0.9 | Ernesto | ☑ | Instalado con `uv`. |
| Node/bun para build de `.web` | Reflex | ☐ | Lo gestiona `reflex run` (primera ejecución). |
| Cuenta GitHub + `gh` autenticado | Ernesto | ☐ | Para `gh repo create`. |

## 3. Fases de Implementación

---

### Fase 1: Fundaciones ✅ (hecho)
**Objetivo:** base del proyecto reproducible.

| ID | Tarea | Estimación | Dependencia | Estado |
|---|---|---|---|---|
| F1-01 | `uv init` + pin Python 3.12 | 0.5d | — | ☑ |
| F1-02 | `uv add reflex` + `reflex init` (blank) | 0.5d | F1-01 | ☑ |
| F1-03 | Estructura de paquetes (`reflex_pragmatic_dnd/`) | 0.5d | F1-02 | ☑ |
| F1-04 | `.gitignore`, README, repo git | 0.5d | F1-01 | ☑ |

**Done:** `uv run reflex run` arranca la app blank; el paquete importa.

---

### Fase 2: Core wrappers ✅ (hecho)
**Objetivo:** envolver el adaptador de elementos.

| ID | Tarea | Estimación | Dependencia | Estado |
|---|---|---|---|---|
| F2-01 | `pragmatic_dnd.jsx`: `PdndDraggable`, `PdndDropTarget`, `PdndMonitor` | 1.5d | F1-03 | ☑ |
| F2-02 | `core.py`: `Draggable`/`DropTarget`/`Monitor` (`NoSSRComponent`) | 1d | F2-01 | ☑ |
| F2-03 | Declarar `lib_dependencies` (`@atlaskit/*`) | 0.25d | F2-02 | ☑ |
| F2-04 | API pública en `__init__.py` | 0.25d | F2-02 | ☑ |
| F2-05 | Verificación: import + render del árbol de componentes | 0.5d | F2-04 | ☑ |

**Done:** los componentes se construyen y `render()` no falla a nivel Reflex.

---

### Fase 3: Suite completa + ejemplo ✅ (hecho parcialmente)
**Objetivo:** hitbox, auto-scroll y demo Kanban.

| ID | Tarea | Estimación | Dependencia | Estado |
|---|---|---|---|---|
| F3-01 | Hitbox de borde más cercano en `PdndDropTarget` | 1d | F2-01 | ☑ |
| F3-02 | `PdndScrollContainer` (auto-scroll) | 0.5d | F2-01 | ☑ |
| F3-03 | App demo Kanban ordenable | 1d | F2-04 | ☑ |
| F3-04 | Ejemplo de lista ordenable (`examples/`) | 0.5d | F3-03 | ☑ |
| F3-05 | Prueba E2E manual `reflex run` en navegador | 0.5d | F3-03 | ☐ |

**Done:** arrastrar tarjetas entre/within columnas reordena el estado.

---

### Fase 4: Pulido, indicador y a11y ☐ (planificado)
**Objetivo:** experiencia completa.

| ID | Tarea | Estimación | Dependencia | Estado |
|---|---|---|---|---|
| F4-01 | Componente `DropIndicator` (react-drop-indicator estilizado) | 1.5d | F3-01 | ☐ |
| F4-02 | Estados visuales (`data-over`, `data-dragging`) documentados con CSS | 0.5d | F3-03 | ☐ |
| F4-03 | Adaptador externo (archivos/URLs) | 2d | F2-01 | ☐ |
| F4-04 | Pruebas (pytest sobre wrappers + Playwright E2E) | 1.5d | F3-05 | ☐ |

**Done:** indicador visible al reordenar; suite de tests verde.

---

### Fase 5: Empaquetado y publicación ☐ (planificado)
**Objetivo:** distribuir.

| ID | Tarea | Estimación | Dependencia | Estado |
|---|---|---|---|---|
| F5-01 | Metadatos de `pyproject.toml` para wheel (incluir `.jsx`) | 0.5d | F4-04 | ☐ |
| F5-02 | `reflex component build` / `publish` a PyPI | 0.5d | F5-01 | ☐ |
| F5-03 | CI (GitHub Actions): lint + build + tests | 1d | F4-04 | ☐ |
| F5-04 | Registro en Reflex Custom Components | 0.25d | F5-02 | ☐ |

**Done:** `pip install reflex-pragmatic-dnd` funciona en un proyecto limpio.

## 4. Criterios de Aceptación Global (v1.0)
- Un usuario construye un Kanban ordenable copiando el ejemplo, sin escribir JS.
- `reflex run` instala automáticamente los paquetes `@atlaskit` en `.web`.
- Los 4 paquetes de la suite están envueltos o expuestos.
- Specs versionados junto al código y referenciados por el plan.

## 5. Dependencias entre Fases

```
F1 ──▶ F2 ──▶ F3 ──▶ F4 ──▶ F5
```
