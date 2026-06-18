# reflex-pragmatic-dnd — Technical Design Document

## Metadata

| Field | Value |
|---|---|
| **Author** | Ernesto (ecrespo) |
| **Status** | `DRAFT` |
| **Version** | 1.0 |
| **Date** | 2026-06-14 |
| **Related PRD** | ../prd/reflex-pragmatic-dnd.md |
| **Related API Spec** | ../api/component-api-v1.md |

---

## 1. Context

Reflex compiles Python components to React and serves a FastAPI backend; state
lives in Python and is synchronized over WebSocket. Pragmatic drag and drop, by
contrast, is imperative: it *attaches* to an `HTMLElement`
(`draggable({element, ...})`) and returns a cleanup function. The technical
challenge is to bridge Reflex's declarative model with Pragmatic's imperative,
refs/effects-based model, while keeping payloads serializable so they can cross
the WebSocket.

The chosen strategy is a **local React glue** (`pragmatic_dnd.jsx`) bundled with
the library via `rx.asset`, plus a set of **Python wrappers**
(`NoSSRComponent`) that expose props and `EventHandler`.

## 2. Technical Goals

- **Correctness:** every effect registers and cleans up its subscription (`return cleanup`) so listeners do not leak between renders.
- **Performance:** the Atlassian JS runs natively on the client; Reflex only receives discrete events (start/drop), not the continuous movement.
- **Maintainability:** a single glue file + thin wrappers; pinned npm versions.
- **Portability:** no SSR dependency; defensive serialization of payloads.

## 3. Proposed Architecture

### 3.1 High-Level Diagram

```
┌─────────────────────────────┐      compiles to     ┌──────────────────────────────┐
│  Reflex App (Python)         │  ───────────────▶    │  React Frontend (.web)        │
│  - rx.State (cards, ...)     │                      │  - PdndDraggable / PdndDrop…  │
│  - dnd.draggable/drop_target │                      │    (pragmatic_dnd.jsx)        │
│  - handle_drop(@rx.event)    │   ◀── WebSocket ───  │  - useEffect + draggable()/   │
└─────────────────────────────┘   on_drop event       │    dropTargetForElements()/   │
                                   (JSON payload)      │    monitorForElements()       │
                                                       └───────────────┬───────────────┘
                                                                       │ uses
                                                       ┌───────────────▼───────────────┐
                                                       │ @atlaskit/pragmatic-drag-and-  │
                                                       │ drop (+ hitbox, auto-scroll,   │
                                                       │ react-drop-indicator)          │
                                                       └────────────────────────────────┘
```

### 3.2 Components

| Component | Technology | Responsibility |
|---|---|---|
| `pragmatic_dnd.jsx` | React (JSX) | Attach Pragmatic to elements via `useEffect`/`useRef`; normalize and emit payloads. |
| `core.py` | Reflex `NoSSRComponent` | Expose `Draggable`/`DropTarget`/`Monitor`/`ScrollContainer` with props and events. |
| `__init__.py` | Python | Public API and factories (`draggable`, …). |
| `lib_dependencies` | npm | Install `@atlaskit/pragmatic-drag-and-drop*` into `.web`. |
| Demo app | Reflex | Sortable Kanban that consumes the library. |

### 3.3 Data Flow

**Flow: dropping a card into another column**

```
1. The user starts dragging a card (PdndDraggable).
2. The glue calls draggable({getInitialData: () => {dragId, ...itemData}}).
3. On entering a DropTarget with hitbox, attachClosestEdge computes the edge.
4. On drop, monitorForElements.onDrop gathers {source, dropTargets}.
5. The glue sanitizes the payload (JSON) and calls onDrop(payload).
6. Reflex sends the event over WebSocket to KanbanState.handle_drop.
7. The handler rebuilds the board immutably and reassigns self.cards.
8. Reflex broadcasts the new state and the frontend re-renders.
```

**Error / edge flow:**

```
1. Dropping outside any target → dropTargets == [] → handler is a no-op.
2. Non-serializable data → discarded by clean() before crossing the socket.
3. Duplicate render → cleanup from the previous useEffect avoids dangling listeners.
```

## 4. Design Decisions

### DD-001: Local JSX glue vs. dedicated npm package
- **Decision:** bundle `pragmatic_dnd.jsx` with `rx.asset(shared=True)` and declare
  the `@atlaskit` dependencies via `lib_dependencies`.
- **Alternatives:** (a) publish a dedicated npm package that re-exports; (b) inject
  everything with `add_hooks` (raw hooks in each wrapper).
- **Rationale:** the local asset avoids an npm publishing chain and keeps the glue
  versioned alongside the Python; raw `add_hooks` is more fragile and harder to read.

### DD-002: `NoSSRComponent`
- **Decision:** all classes inherit from `NoSSRComponent`.
- **Rationale:** Pragmatic uses `document`/`window`; the dynamic import avoids SSR failures.

### DD-003: Discrete events, not movement streaming
- **Decision:** only `start`/`enter`/`leave`/`drop` events cross the WebSocket.
- **Rationale:** the continuous computation (position, edge) happens on the client; sending every
  `onDrag` would saturate the socket. The Python state only changes on drop.

### DD-004: Monitor as the single source of truth for boards
- **Decision:** recommend a single `monitor(on_drop=...)` per board instead of a
  handler per card.
- **Rationale:** simplifies the relocation logic and reduces props per item.

## 5. Repository Structure

```
reflex-pragmatic-drag-and-drop/
├── reflex_pragmatic_dnd/            # LIBRARY
│   ├── __init__.py                  # public API
│   ├── core.py                      # NoSSRComponent wrappers
│   └── pragmatic_dnd.jsx            # React glue (rx.asset)
├── reflex_pragmatic_drag_and_drop/  # DEMO APP (Kanban)
│   └── reflex_pragmatic_drag_and_drop.py
├── examples/                        # additional examples (sortable list)
├── specs/                           # this SDD documentation
├── rxconfig.py
└── pyproject.toml
```

## 6. Risks and Mitigations

| Risk | Impact | Mitigation |
|---|---|---|
| API changes in `@atlaskit` | Breakage on update | Pinned versions (`^1.x`), build smoke tests. |
| Reflex changes the asset pattern | Glue does not load | Cover with CI against the supported Reflex version. |
| Large payloads | Latency | `item_data` must be small; documented in the API Spec. |
| Incorrect reordering with unstable ids | Broken UX | Explicit requirement for stable `drag_id`/`drop_id`. |
