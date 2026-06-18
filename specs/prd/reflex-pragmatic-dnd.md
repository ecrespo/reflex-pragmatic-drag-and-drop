# reflex-pragmatic-drag-and-drop

## Product Requirements Document (PRD)

| Field | Value |
|---|---|
| **Author** | Ernesto (ecrespo) |
| **Status** | `DRAFT` |
| **Version** | 1.0 |
| **Date** | 2026-06-14 |
| **Reviewers** | — |
| **Last updated** | 2026-06-14 |

---

## 1. Executive Summary

`reflex-pragmatic-drag-and-drop` is a component library for [Reflex](https://reflex.dev)
that exposes, in pure Python, the capabilities of Atlassian's
[Pragmatic drag and drop](https://github.com/atlassian/pragmatic-drag-and-drop):
a low-level, framework-agnostic drag-and-drop *toolchain*
built on top of the browser's native drag and drop API.

The goal is for a Reflex developer to be able to build drag and drop
experiences (sortable lists, Kanban boards, tree reordering,
auto-scroll) **without writing JavaScript**, using idiomatic Reflex
components and event handlers. The library wraps the complete family of
`@atlaskit/pragmatic-drag-and-drop-*` packages (core, hitbox, auto-scroll,
react-drop-indicator).

## 2. Context and Problem

### 2.1 Current Situation
Reflex does not include drag and drop primitives. Anyone who needs them must
manually wrap a React JS library (HTML5 DnD, dnd-kit, react-dnd…) following
the "Wrapping React" flow, which requires knowledge of React, hooks, and the
Reflex assets system.

### 2.2 Problem
Pragmatic drag and drop is today one of the best options (performance, size,
accessibility, framework independence), but its API is designed to
imperatively attach behavior to DOM elements via `useEffect` and
cleanup functions. Porting that model to Reflex (state in Python,
declarative rendering) is not trivial and gets reimplemented over and over.

### 2.3 Opportunity
Package the React→Reflex *glue* once and publish it as a reusable
library: a stable Python API, serializable events, and ready-to-copy
examples (Kanban, sortable list).

## 3. Target Users

### Persona 1: Reflex product developer
- **Description:** builds dashboards and internal tools with Reflex.
- **Primary need:** reorderable boards and lists without touching JS.
- **Usage frequency:** recurring during feature development.
- **Technical level:** medium (high Python, low JS).

### Persona 2: Maintainer of Reflex component libraries
- **Description:** publishes components for the Reflex community.
- **Primary need:** a reference pattern for wrapping JS libraries
  based on refs/effects and exposing them with typed events.
- **Technical level:** high.

## 4. Goals and Success Metrics

### 4.1 Product Goals

| Goal | Metric | Target | Deadline |
|---|---|---|---|
| Cover the full suite | `@atlaskit` packages wrapped | 4/4 (core, hitbox, auto-scroll, drop-indicator) | v1.0 |
| Fast onboarding | Time to first working board | < 15 min by copying the example | v1.0 |
| Zero JS for the user | Lines of JS in the user's app | 0 | v1.0 |

### 4.2 User Goals

| User Goal | Indicator |
|---|---|
| Create a sortable list | `draggable` + `drop_target(with_closest_edge=True)` API |
| Move items between containers | A single `monitor(on_drop=...)` |
| Automatic scroll in long lists | `scroll_container` |

## 5. Scope

### 5.1 In Scope
- [x] `Draggable` component (registers an element as draggable, with `item_data`).
- [x] `DropTarget` component (drop target, with closest-edge hitbox).
- [x] `Monitor` component (global listener for drag operations).
- [x] `ScrollContainer` component (auto-scroll during the drag).
- [x] Events: `on_drag_start`, `on_drop`, `on_drag_enter`, `on_drag_leave`.
- [x] Packaging of the JSX *glue* via `rx.asset` + declared npm dependencies.
- [x] Sortable Kanban example and list example.

### 5.2 Out of Scope
- Text and external file adapters (`text/adapter`, external) — future iteration.
- Advanced *styled* drop indicators with `react-drop-indicator` (the edge is exposed; rendering the indicator is the user's responsibility in v1.0).
- Keyboard support / advanced accessibility beyond what the core provides.
- State persistence (responsibility of the user's app).

### 5.3 Future Considerations
- Styled `DropIndicator` component wrapping `@atlaskit/...-react-drop-indicator`.
- External adapter (dragging files/URLs from outside the browser).
- Publication on PyPI as `reflex-pragmatic-dnd` and registration in the Reflex component registry.

## 6. Functional Requirements

### RF-001: Declare a draggable element
- **Description:** the system must allow marking any component subtree as draggable and attaching data to it.
- **Actor:** developer.
- **Preconditions:** component mounted on the client (NoSSR).
- **Main flow:** `draggable(child, drag_id=..., item_data={...})` → when the drag starts/ends, `on_drag_start`/`on_drop` are emitted with the payload.
- **Acceptance criterion:** the Python handler receives `dragId` and `item_data`.

### RF-002: Declare a drop target with edge
- **Description:** register a drop target that, optionally, reports the closest edge (top/bottom/left/right) for reordering.
- **Acceptance criterion:** `on_drop` includes `closestEdge`, `source`, and `target`.

### RF-003: Global listening with Monitor
- **Description:** a single component with no DOM footprint that reports the `source` and the `dropTargets` stack of each operation.
- **Acceptance criterion:** a single handler can relocate an item into any column.

### RF-004: Auto-scroll
- **Description:** a container that scrolls automatically when dragging near its edges.
- **Acceptance criterion:** lists taller than the viewport scroll during the drag.

## 7. Non-Functional Requirements
- **RNF-01 (Compatibility):** Reflex ≥ 0.9, Python ≥ 3.12.
- **RNF-02 (Zero user JS):** all JS logic lives in the packaged *glue*.
- **RNF-03 (Serializable):** every event payload must be JSON-serializable (sanitized on the client).
- **RNF-04 (SSR-safe):** the components are `NoSSRComponent` (they use `document`).
