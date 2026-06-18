"""Example: a single sortable list using reflex_pragmatic_dnd.

This is a self-contained Reflex page. To run it as the app, point `rxconfig.py`
`app_name` at a module that exposes `app`, or copy `index` into your own app.
"""

from __future__ import annotations

import reflex as rx

import reflex_pragmatic_dnd as dnd


class ListState(rx.State):
    items: list[dict] = [
        {"id": "a", "label": "🍎 Apple"},
        {"id": "b", "label": "🍌 Banana"},
        {"id": "c", "label": "🍒 Cherry"},
        {"id": "d", "label": "🥝 Kiwi"},
    ]

    @rx.event
    def reorder(self, payload: dict):
        # Delegates to the tested pure reducer (reflex_pragmatic_dnd.reorder).
        self.items = dnd.reorder_list(self.items, payload)


def row(item: rx.Var) -> rx.Component:
    return dnd.draggable(
        dnd.drop_target(
            rx.text(item["label"], size="3"),
            drop_id=item["id"],
            target_data={"id": item["id"]},
            with_closest_edge=True,
            allowed_edges=["top", "bottom"],
            width="100%",
        ),
        drag_id=item["id"],
        item_data={"id": item["id"]},
        cursor="grab",
        padding="10px 14px",
        margin_bottom="6px",
        border="1px solid var(--gray-5)",
        border_radius="8px",
        background="var(--gray-2)",
    )


def index() -> rx.Component:
    return rx.center(
        dnd.monitor(on_drop=ListState.reorder),
        rx.vstack(
            rx.heading("Sortable list", size="6"),
            rx.foreach(ListState.items, row),
            width="320px",
            spacing="2",
        ),
        padding_y="3em",
    )


app = rx.App()
app.add_page(index)
