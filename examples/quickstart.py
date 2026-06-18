"""Quickstart: the smallest app a consumer writes after installing from PyPI.

    uv add reflex-pragmatic-drag-and-drop     # or: pip install ...

Then point `rxconfig.py` `app_name` at this module (or copy `index` into your
own app) and run `reflex run`. Verified end-to-end against the published 0.1.1
wheel: `reflex export --frontend-only` installs the `@atlaskit/*` packages and
compiles the bundled glue into a production build.
"""

from __future__ import annotations

import reflex as rx

import reflex_pragmatic_dnd as dnd


class State(rx.State):
    items: list[str] = ["Apple", "Banana", "Cherry"]
    last: str = ""

    @rx.event
    def on_drop(self, payload: dict):
        # `reorder_list` is the tested pure reducer shipped with the package.
        self.items = dnd.reorder_list(self.items, payload)
        self.last = str(payload)


def row(item: rx.Var) -> rx.Component:
    return dnd.draggable(
        dnd.drop_target(
            rx.text(item, size="3"),
            drop_id=item,
            target_data={"id": item},
            with_closest_edge=True,
            allowed_edges=["top", "bottom"],
        ),
        drag_id=item,
        item_data={"id": item},
        cursor="grab",
        padding="8px",
        border="1px solid var(--gray-5)",
        margin_bottom="6px",
    )


def index() -> rx.Component:
    return rx.container(
        # One global listener routes every drop to the state handler.
        dnd.monitor(on_drop=State.on_drop),
        rx.heading("Pragmatic DnD quickstart", size="6"),
        rx.foreach(State.items, row),
        rx.text(State.last, color="var(--gray-11)", size="1"),
        padding="2em",
    )


app = rx.App()
app.add_page(index)
