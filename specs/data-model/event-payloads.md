# reflex-pragmatic-dnd — Data Model Specification

## Metadata

| Field | Value |
|---|---|
| **Author** | Ernesto (ecrespo) |
| **Status** | `DRAFT` |
| **Version** | 1.0 |
| **Date** | 2026-06-14 |
| **Storage** | In memory (`rx.State`) — no database |
| **Related Tech Design** | ../technical/architecture.md |

---

## 1. Model Overview

This library does not persist data: the "data model" consists of (a) the **event
payloads** that travel over the WebSocket from client→server and (b) the **application
state** that the developer maintains in `rx.State`. All payloads are JSON.

```
Draggable ──(getInitialData)──▶ source        ┐
DropTarget ─(getData+hitbox)──▶ target/edge   ├─▶ Monitor.onDrop ─▶ rx.State (Python)
                                              ┘
```

## 2. Payload Structures

### 2.1 `SourceData` (data of the dragged item)

Built by `Draggable.getInitialData`. Base shape + whatever the user passes in `item_data`.

```json
{
  "dragId": "string (== component's drag_id)",
  "...itemData": "arbitrary keys provided by the user"
}
```

| Field | Type | Source | Notes |
|---|---|---|---|
| `dragId` | string | `drag_id` | Required, stable. |
| `*` (extra) | JSON | `item_data` | Small and serializable. |

### 2.2 `TargetData` (data of the drop target)

Built by `DropTarget.getData`; if `with_closest_edge`, it includes the edge symbol
(extracted as a string in the payloads).

```json
{
  "dropId": "string (== drop_id)",
  "...targetData": "arbitrary keys provided by the user",
  "closestEdge": "top | bottom | left | right | null"
}
```

### 2.3 `Monitor.on_drop` payload

```json
{
  "source": { "dragId": "c1", "cardId": "c1" },
  "dropTargets": [
    { "dropId": "c4", "kind": "card", "cardId": "c4", "closestEdge": "bottom" },
    { "dropId": "doing", "kind": "column", "column": "doing" }
  ],
  "target": { "dropId": "c4", "kind": "card", "cardId": "c4", "closestEdge": "bottom" }
}
```

| Field | Type | Description |
|---|---|---|
| `source` | object | `SourceData` of the dragged item. |
| `dropTargets` | array | Targets traversed, **from innermost to outermost**. |
| `target` | object\|null | `dropTargets[0]` for convenience. |

### 2.4 `DropTarget.on_drop` / `on_drag_enter` payload

```json
{ "dropId": "z", "closestEdge": "top|null", "source": { }, "target": { } }
```

## 3. Reference Application State (Kanban demo)

Defined by the user in `rx.State` (not by the library). Documented here to
show the consumption pattern.

```python
cards: dict[str, list[dict]] = {
    "todo":  [{"id": "c1", "title": "..."}],
    "doing": [{"id": "c4", "title": "..."}],
    "done":  [{"id": "c5", "title": "..."}],
}
```

| Entity | Shape | Relationship |
|---|---|---|
| `Column` | string key (`todo`/`doing`/`done`) | 1:N with `Card` |
| `Card` | `{ "id": str, "title": str }` | belongs to a column |

### Invariants
- `Card.id` unique across the whole board (required for `drag_id`).
- The order within each list **is** the visual order (index = position).
- Mutations reassign `self.cards` (Reflex detects changes by reassignment, not by in-place mutation).

## 4. Transformation Rules (handle_drop)

```
input: payload (section 2.3)
1. source.cardId required and dropTargets non-empty, otherwise → no-op.
2. to_col = (col_target ?? card_target).column ; must exist in COLUMNS.
3. Rebuild board immutably; extract the card by id.
4. If card_target and card_target.cardId != source.cardId:
     idx = position of card_target.cardId
     if closestEdge == "bottom": idx += 1
     insert at idx
   otherwise: append to the end of to_col.
5. self.cards = board   # reassignment → reactivity
```

## 5. Serialization Considerations

- The client applies `JSON.parse(JSON.stringify(...))` (`clean()`); any non-serializable
  value (functions, symbols, circular references) is discarded.
- The closest edge is a `Symbol` in Pragmatic; it is exported as a `string` so it can
  cross the socket.
- Keep `item_data`/`target_data` small (ids and metadata), not heavy objects.
