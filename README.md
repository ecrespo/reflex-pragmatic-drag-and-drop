# reflex-pragmatic-drag-and-drop

[Reflex](https://reflex.dev) bindings for Atlassian's
[Pragmatic drag and drop](https://github.com/atlassian/pragmatic-drag-and-drop).
Build sortable lists and Kanban boards in **pure Python**, without writing
JavaScript.

Wraps the full suite: `@atlaskit/pragmatic-drag-and-drop` (core),
`-hitbox` (closest edge), `-auto-scroll`, and `-react-drop-indicator`.

## Status

Functional core (Phases 1–3 of the plan) with a test suite. See [`specs/`](specs/)
for the complete design (PRD, API, Tech Design, Data Model, Plan).

## Requirements

- Python ≥ 3.12 · Reflex ≥ 0.9 · [`uv`](https://docs.astral.sh/uv/) package manager

## Installation and running (Kanban demo)

```bash
uv sync                 # installs Python dependencies
uv run reflex run       # installs @atlaskit packages in .web and starts on :3000
```

Open http://localhost:3000 and drag the cards between columns.

## Usage

```python
import reflex as rx
import reflex_pragmatic_dnd as dnd


class State(rx.State):
    msg: str = ""

    @rx.event
    def on_drop(self, payload: dict):
        self.msg = f"{payload['source']} -> {payload.get('target')}"


def index():
    return rx.box(
        # Global listener: a single handler for the whole page.
        dnd.monitor(on_drop=State.on_drop),

        # A draggable element that carries data.
        dnd.draggable(
            rx.text("Drag me"),
            drag_id="card-1",
            item_data={"cardId": "card-1"},
        ),

        # A drop target with edge detection (for reordering).
        dnd.drop_target(
            rx.text("Drop it here"),
            drop_id="zone-1",
            target_data={"kind": "zone"},
            with_closest_edge=True,
            allowed_edges=["top", "bottom"],
        ),

        rx.text(State.msg),
    )
```

### Components

| Factory | Wraps | Events |
|---|---|---|
| `dnd.draggable(...)` | `draggable` (element adapter) | `on_drag_start`, `on_drop` |
| `dnd.drop_target(...)` | `dropTargetForElements` (+ hitbox) | `on_drag_enter`, `on_drag_leave`, `on_drop` |
| `dnd.monitor(...)` | `monitorForElements` | `on_drag_start`, `on_drop` |
| `dnd.scroll_container(...)` | `autoScrollForElements` | — |

Full details on props and payloads: [`specs/api/component-api-v1.md`](specs/api/component-api-v1.md).

### State reducers (optional)

The library includes two pure functions that transform the payload of
`monitor(on_drop=...)` into the new state, implementing the rules of
[`specs/data-model/event-payloads.md`](specs/data-model/event-payloads.md) §4.
They do not mutate their inputs and return the original object unchanged on a no-op
(dropping outside, onto itself, or onto an unknown column):

```python
@rx.event
def handle_drop(self, payload: dict):
    self.cards = dnd.move_card(self.cards, payload, columns=["todo", "doing", "done"])

@rx.event
def reorder(self, payload: dict):
    self.items = dnd.reorder_list(self.items, payload)
```

### Visual states (CSS)

`drop_target` exposes attributes on the DOM for styling during the drag, and
`draggable` marks the element in progress:

| Attribute | Value | Component |
|---|---|---|
| `data-dragging` | `true`/`false` | `draggable` |
| `data-over` | `true`/`false` | `drop_target` |
| `data-closest-edge` | `top`/`bottom`/`left`/`right`/`""` | `drop_target` (with `with_closest_edge`) |
| `data-drop-id` | the `drop_id` | `drop_target` |

```python
dnd.drop_target(
    rx.text("Drop it here"),
    drop_id="zone-1",
    with_closest_edge=True,
    # Highlight the target and draw a line on the closest edge.
    style={
        "&[data-over='true']": {"background": "var(--accent-3)"},
        "&[data-closest-edge='top']": {"box_shadow": "inset 0 2px 0 var(--accent-9)"},
        "&[data-closest-edge='bottom']": {"box_shadow": "inset 0 -2px 0 var(--accent-9)"},
    },
)
```

## Examples

- **Sortable Kanban:** [`reflex_pragmatic_drag_and_drop/reflex_pragmatic_drag_and_drop.py`](reflex_pragmatic_drag_and_drop/reflex_pragmatic_drag_and_drop.py) (default app).
- **Sortable list:** [`examples/sortable_list.py`](examples/sortable_list.py).

## Structure

```
reflex_pragmatic_dnd/            # the library (wrappers + JSX glue)
reflex_pragmatic_drag_and_drop/  # Kanban demo app
examples/                        # additional examples
specs/                           # SDD documentation
```

## How it works

A local React *glue* (`pragmatic_dnd.jsx`, bundled with `rx.asset`) attaches
Pragmatic to the DOM elements via `useEffect`/`useRef` and emits JSON-serializable
payloads. `NoSSRComponent` wrappers expose them as Reflex components with typed
events. Only discrete events (start/drop) cross the WebSocket; the continuous
computation happens on the client. See
[`specs/technical/architecture.md`](specs/technical/architecture.md).

## Tests

```bash
uv run pytest
```

Covers the pure reducers (transformation rules from Data Model §4 and edge cases
from API Spec §4), the states of the demo/example app, and the wrapper contract
(tags, snake↔camel props, events, `NoSSRComponent`, pinned `@atlaskit`
dependencies).

## License

MIT.
