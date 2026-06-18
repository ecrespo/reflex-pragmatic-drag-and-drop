# reflex-pragmatic-dnd — Component API Specification

## Metadata

| Field | Value |
|---|---|
| **Author** | Ernesto (ecrespo) |
| **Status** | `DRAFT` |
| **API Version** | v1.0 |
| **Date** | 2026-06-14 |
| **Related PRD** | ../prd/reflex-pragmatic-dnd.md |

---

## 1. Overview

The "API" of this library is its **Python component surface**: the classes and
factories the developer imports from `reflex_pragmatic_dnd`, their props and
their event handlers. It acts as the contract between the library and the user's
app. There is no HTTP API.

Import:

```python
import reflex_pragmatic_dnd as dnd
# dnd.draggable, dnd.drop_target, dnd.monitor, dnd.scroll_container
```

## 2. Components

### 2.1 `draggable(*children, **props)` → `Draggable`

Wraps `@atlaskit/pragmatic-drag-and-drop/element/adapter#draggable`.

| Prop | Python Type | Required | Description |
|---|---|---|---|
| `drag_id` | `str` | Yes | Stable identifier for the item; travels in every event. |
| `item_data` | `dict` | No | Arbitrary JSON-serializable payload attached to the drag. |
| `drag_handle_selector` | `str` | No | Internal CSS selector used as the "handle"; defaults to the whole element. |

**Events**

| Event | Payload | When |
|---|---|---|
| `on_drag_start` | `{ "dragId": str, "itemData": dict }` | The drag begins. |
| `on_drop` | `{ "dragId": str, "itemData": dict }` | It ends (dropped or canceled). |

### 2.2 `drop_target(*children, **props)` → `DropTarget`

Wraps `dropTargetForElements` + (optional) `@atlaskit/pragmatic-drag-and-drop-hitbox/closest-edge`.

| Prop | Python Type | Required | Description |
|---|---|---|---|
| `drop_id` | `str` | Yes | Identifier of the target. |
| `target_data` | `dict` | No | Target data, included in the drop payload. |
| `with_closest_edge` | `bool` | No (default `False`) | Enables the closest-edge hitbox. |
| `allowed_edges` | `list[str]` | No (default `["top","bottom"]`) | Edges considered: `top`/`bottom`/`left`/`right`. |

**Events**

| Event | Payload | When |
|---|---|---|
| `on_drag_enter` | `{ "dropId", "closestEdge"\|null, "source": dict }` | The pointer enters the target. |
| `on_drag_leave` | `{ "dropId" }` | The pointer leaves. |
| `on_drop` | `{ "dropId", "closestEdge"\|null, "source": dict, "target": dict }` | It is dropped on the target. |

**DOM attributes exposed for styling (CSS):**
`data-over="true|false"`, `data-closest-edge="top|bottom|..."`, `data-drop-id`.

### 2.3 `monitor(**props)` → `Monitor`

Wraps `monitorForElements`. Renders no visible footprint.

**Events**

| Event | Payload | When |
|---|---|---|
| `on_drag_start` | `{ "source": dict }` | Any drag on the page begins. |
| `on_drop` | `{ "source": dict, "dropTargets": list[dict], "target": dict\|null }` | Any drag ends. `dropTargets[0]` is the innermost target. |

### 2.4 `scroll_container(*children, **props)` → `ScrollContainer`

Wraps `combine(dropTargetForElements, autoScrollForElements)`. Auto-scrolls
while dragging near the container edges. No events of its own in v1.0.

## 3. Conventions

- **Serialization:** the *glue* applies `JSON.parse(JSON.stringify(...))` to every
  payload before sending it to Python; non-serializable values are discarded.
- **Naming:** props in `snake_case` (Python) ↔ React props in `camelCase`
  (automatic Reflex mapping). The keys *inside* the payloads use `camelCase`
  (`dragId`, `closestEdge`) because they come from the JS side.
- **Identifiers:** `drag_id`/`drop_id` must be unique and stable across
  renders so that reordering works correctly.

## 4. Errors and Edge Cases

| Case | Expected behavior |
|---|---|
| Dropping outside any `DropTarget` | `Monitor.on_drop` with `dropTargets == []`; the handler should ignore it. |
| `item_data` with non-serializable objects | They are silently discarded (client-side sanitization). |
| Dropping an item onto itself | `target.cardId == source.cardId`; the handler should no-op. |
| Component rendered under SSR | Avoided: the classes are `NoSSRComponent` (dynamic import). |

## 5. Minimal example (the contract in use)

```python
import reflex as rx
import reflex_pragmatic_dnd as dnd

class S(rx.State):
    msg: str = ""
    @rx.event
    def on_drop(self, payload: dict):
        self.msg = f"{payload['source']} -> {payload.get('target')}"

def page():
    return rx.box(
        dnd.monitor(on_drop=S.on_drop),
        dnd.draggable(rx.text("Drag me"), drag_id="a", item_data={"cardId": "a"}),
        dnd.drop_target(rx.text("Drop it here"), drop_id="z",
                        target_data={"kind": "zone"}),
        rx.text(S.msg),
    )
```
