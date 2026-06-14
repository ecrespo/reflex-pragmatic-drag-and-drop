"""Reflex wrappers around Atlassian's Pragmatic drag and drop.

Each class below wraps a React component defined in ``pragmatic_dnd.jsx`` and
exposes a Pythonic API plus Reflex event handlers. The JS glue is bundled with
``rx.asset`` so no separate npm publish of the glue is required; the underlying
``@atlaskit/*`` packages are declared through ``lib_dependencies`` and installed
by Reflex into the ``.web`` directory on first build.
"""

from __future__ import annotations

import reflex as rx
from reflex.components.component import NoSSRComponent

# Bundle the JS glue next to this file. `shared=True` copies it into the
# generated frontend's public assets so it can be imported as a local module.
_JSX_PATH = rx.asset("pragmatic_dnd.jsx", shared=True)

# Pinned versions of the Pragmatic drag and drop packages (full suite).
_LIB_DEPS: list[str] = [
    "@atlaskit/pragmatic-drag-and-drop@^1.8.1",
    "@atlaskit/pragmatic-drag-and-drop-hitbox@^1.1.0",
    "@atlaskit/pragmatic-drag-and-drop-auto-scroll@^2.1.5",
    "@atlaskit/pragmatic-drag-and-drop-react-drop-indicator@^3.2.10",
]


class _PdndBase(NoSSRComponent):
    """Shared base: same local library + npm dependencies for every wrapper.

    Pragmatic drag and drop touches ``document``/``window`` directly, so the
    components must be client-side only -> ``NoSSRComponent``.
    """

    library = f"$/public{_JSX_PATH}"
    lib_dependencies: list[str] = _LIB_DEPS


class Draggable(_PdndBase):
    """Make the wrapped content draggable and attach arbitrary ``item_data``."""

    tag = "PdndDraggable"

    # Stable identifier for the dragged item (sent back on every event).
    drag_id: rx.Var[str]
    # Arbitrary JSON-serialisable payload travelling with the drag.
    item_data: rx.Var[dict]
    # Optional CSS selector inside the element to use as the drag handle.
    drag_handle_selector: rx.Var[str]

    # Fired when the drag starts / ends. Payload: {"dragId", "itemData"}.
    on_drag_start: rx.EventHandler[lambda e: [e]]
    on_drop: rx.EventHandler[lambda e: [e]]


class DropTarget(_PdndBase):
    """Register a drop target, optionally with closest-edge hitbox detection."""

    tag = "PdndDropTarget"

    drop_id: rx.Var[str]
    target_data: rx.Var[dict]
    # When True, the drop payload includes the closest edge ("top"/"bottom"/...).
    with_closest_edge: rx.Var[bool]
    allowed_edges: rx.Var[list[str]]

    # Payloads carry {"dropId", "closestEdge", "source", "target"}.
    on_drag_enter: rx.EventHandler[lambda e: [e]]
    on_drag_leave: rx.EventHandler[lambda e: [e]]
    on_drop: rx.EventHandler[lambda e: [e]]


class Monitor(_PdndBase):
    """Page-level listener for all drag operations (no DOM footprint).

    The drop payload exposes ``source`` and the list of ``dropTargets`` hit, so a
    single handler can update application state for an entire board.
    """

    tag = "PdndMonitor"

    on_drag_start: rx.EventHandler[lambda e: [e]]
    on_drop: rx.EventHandler[lambda e: [e]]


class ScrollContainer(_PdndBase):
    """Container that auto-scrolls while an item is dragged over its edges."""

    tag = "PdndScrollContainer"


# Convenience factory functions (Reflex idiom: lowercase callables).
draggable = Draggable.create
drop_target = DropTarget.create
monitor = Monitor.create
scroll_container = ScrollContainer.create
