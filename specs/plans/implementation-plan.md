# reflex-pragmatic-drag-and-drop — Implementation Plan

## Metadata

| Field | Value |
|---|---|
| **Author** | Ernesto (ecrespo) |
| **Status** | `IN_PROGRESS` |
| **Version** | 1.0 |
| **Date** | 2026-06-14 |
| **PRD** | ../prd/reflex-pragmatic-dnd.md |
| **Tech Design** | ../technical/architecture.md |
| **Data Model** | ../data-model/event-payloads.md |
| **API Spec** | ../api/component-api-v1.md |

---

## 1. Implementation Summary

Incremental build in 5 phases, from the project foundation to packaging for
PyPI. The core (Phases 1-3) is already implemented in this repository; Phases 4-5
remain as planned work. Approach: wrap the core first, validate with a real
example (Kanban), then add hitbox/auto-scroll and, finally, polish and
publish.

**Total estimated duration:** ~3 sprints (1 dev).
**Target date for v1.0:** TBD.

## 2. Prerequisites

| Prerequisite | Owner | Status | Notes |
|---|---|---|---|
| Approved specs (PRD/API/Tech/Data) | Ernesto | ☑ Draft ready | This `specs/` directory. |
| Toolchain: `uv`, Python 3.12, Reflex 0.9 | Ernesto | ☑ | Installed with `uv`. |
| Node/bun for `.web` build | Reflex | ☐ | Managed by `reflex run` (first run). |
| GitHub account + authenticated `gh` | Ernesto | ☐ | For `gh repo create`. |

## 3. Implementation Phases

---

### Phase 1: Foundations ✅ (done)
**Goal:** reproducible project foundation.

| ID | Task | Estimate | Dependency | Status |
|---|---|---|---|---|
| F1-01 | `uv init` + pin Python 3.12 | 0.5d | — | ☑ |
| F1-02 | `uv add reflex` + `reflex init` (blank) | 0.5d | F1-01 | ☑ |
| F1-03 | Package structure (`reflex_pragmatic_dnd/`) | 0.5d | F1-02 | ☑ |
| F1-04 | `.gitignore`, README, git repo | 0.5d | F1-01 | ☑ |

**Done:** `uv run reflex run` starts the blank app; the package imports.

---

### Phase 2: Core wrappers ✅ (done)
**Goal:** wrap the element adapter.

| ID | Task | Estimate | Dependency | Status |
|---|---|---|---|---|
| F2-01 | `pragmatic_dnd.jsx`: `PdndDraggable`, `PdndDropTarget`, `PdndMonitor` | 1.5d | F1-03 | ☑ |
| F2-02 | `core.py`: `Draggable`/`DropTarget`/`Monitor` (`NoSSRComponent`) | 1d | F2-01 | ☑ |
| F2-03 | Declare `lib_dependencies` (`@atlaskit/*`) | 0.25d | F2-02 | ☑ |
| F2-04 | Public API in `__init__.py` | 0.25d | F2-02 | ☑ |
| F2-05 | Verification: import + render of the component tree | 0.5d | F2-04 | ☑ |

**Done:** the components build and `render()` does not fail at the Reflex level.

---

### Phase 3: Full suite + example ✅ (partially done)
**Goal:** hitbox, auto-scroll, and Kanban demo.

| ID | Task | Estimate | Dependency | Status |
|---|---|---|---|---|
| F3-01 | Closest-edge hitbox in `PdndDropTarget` | 1d | F2-01 | ☑ |
| F3-02 | `PdndScrollContainer` (auto-scroll) | 0.5d | F2-01 | ☑ |
| F3-03 | Sortable Kanban demo app | 1d | F2-04 | ☑ |
| F3-04 | Sortable list example (`examples/`) | 0.5d | F3-03 | ☑ |
| F3-05 | Manual E2E test `reflex run` in the browser | 0.5d | F3-03 | ☐ |

**Done:** dragging cards between/within columns reorders the state.

---

### Phase 4: Polish, indicator, and a11y ☐ (planned)
**Goal:** complete experience.

| ID | Task | Estimate | Dependency | Status |
|---|---|---|---|---|
| F4-01 | `DropIndicator` component (styled react-drop-indicator) | 1.5d | F3-01 | ☐ |
| F4-02 | Visual states (`data-over`, `data-dragging`) documented with CSS | 0.5d | F3-03 | ☑ (README) |
| F4-03 | External adapter (files/URLs) | 2d | F2-01 | ☐ |
| F4-04 | Tests (pytest over wrappers + Playwright E2E) | 1.5d | F3-05 | ◑ pytest ☑ / Playwright ☐ |

**Done:** indicator visible while reordering; test suite green.

**Implementation note (pytest):** the reordering logic from Data Model §4 was
extracted to `reflex_pragmatic_dnd/reorder.py` (`move_card`, `reorder_list`) as
pure functions and developed with TDD. Tests in `tests/`:
`test_reorder.py` (reducers + API §4 edge cases), `test_demo_state.py`
(Reflex states of the demo/example), `test_components.py` (wrapper contract).
A discrepancy was discovered and fixed: dropping a card onto itself is now a
no-op (API §4); previously it sent the card to the end of the column.

---

### Phase 5: Packaging and publishing ☐ (planned)
**Goal:** distribute.

| ID | Task | Estimate | Dependency | Status |
|---|---|---|---|---|
| F5-01 | `pyproject.toml` metadata for the wheel (include `.jsx`) | 0.5d | F4-04 | ☑ (hatchling) |
| F5-02 | `reflex component build` / `publish` to PyPI | 0.5d | F5-01 | ☐ |
| F5-03 | CI (GitHub Actions): lint + build + tests | 1d | F4-04 | ☐ |
| F5-04 | Registration in Reflex Custom Components | 0.25d | F5-02 | ☐ |

**Done:** `pip install reflex-pragmatic-dnd` works in a clean project.

## 4. Global Acceptance Criteria (v1.0)
- A user builds a sortable Kanban by copying the example, without writing any JS.
- `reflex run` automatically installs the `@atlaskit` packages into `.web`.
- All 4 packages in the suite are wrapped or exposed.
- Specs versioned alongside the code and referenced by the plan.

## 5. Dependencies Between Phases

```
F1 ──▶ F2 ──▶ F3 ──▶ F4 ──▶ F5
```