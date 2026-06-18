"""Demo app: a sortable Kanban board built with reflex_pragmatic_dnd.

Run with:  uv run reflex run
"""

from __future__ import annotations

import reflex as rx

import reflex_pragmatic_dnd as dnd

COLUMNS = ["todo", "doing", "done"]
COLUMN_TITLES = {"todo": "📋 To do", "doing": "🚧 Doing", "done": "✅ Done"}


class KanbanState(rx.State):
    """Board state: an ordered list of cards per column."""

    cards: dict[str, list[dict]] = {
        "todo": [
            {"id": "c1", "title": "Design the data model"},
            {"id": "c2", "title": "Write the SDD spec"},
            {"id": "c3", "title": "Wrap the React glue"},
        ],
        "doing": [
            {"id": "c4", "title": "Implement DropTarget"},
        ],
        "done": [
            {"id": "c5", "title": "Scaffold with uv"},
        ],
    }
    last_event: str = ""

    @rx.event
    def handle_drop(self, payload: dict):
        """Global drop handler fed by the Monitor component.

        The reordering logic lives in the tested, pure ``move_card`` reducer
        (see ``reflex_pragmatic_dnd/reorder.py`` and data-model §4).
        """
        new_cards = dnd.move_card(self.cards, payload, columns=COLUMNS)
        if new_cards is self.cards:
            return  # no-op (drop outside a target, onto self, etc.)

        # Reassign so Reflex detects the change and report what moved.
        card_id = (payload.get("source") or {}).get("cardId")
        moved = next(
            (
                c
                for col in COLUMNS
                for c in new_cards[col]
                if c["id"] == card_id
            ),
            None,
        )
        dest = next(
            (col for col in COLUMNS if any(c["id"] == card_id for c in new_cards[col])),
            None,
        )
        self.cards = new_cards
        if moved and dest:
            self.last_event = f"Moved '{moved['title']}' -> {COLUMN_TITLES[dest]}"


def card(item: rx.Var) -> rx.Component:
    """A draggable + drop-target card (the drop target enables reordering)."""
    return dnd.draggable(
        dnd.drop_target(
            rx.box(rx.text(item["title"], size="2"), width="100%"),
            drop_id=item["id"],
            target_data={"kind": "card", "cardId": item["id"]},
            with_closest_edge=True,
            allowed_edges=["top", "bottom"],
        ),
        drag_id=item["id"],
        item_data={"cardId": item["id"]},
        cursor="grab",
        background="var(--gray-2)",
        border="1px solid var(--gray-5)",
        border_radius="8px",
        padding="10px",
        margin_bottom="8px",
        _hover={"border_color": "var(--accent-8)"},
    )


def column(col_id: str) -> rx.Component:
    """A column is a drop target (append) holding draggable cards."""
    return dnd.drop_target(
        rx.vstack(
            rx.heading(COLUMN_TITLES[col_id], size="3", margin_bottom="8px"),
            rx.foreach(KanbanState.cards[col_id], card),
            rx.box(height="20px"),  # bottom drop zone padding
            align="stretch",
            width="260px",
            min_height="320px",
        ),
        drop_id=col_id,
        target_data={"kind": "column", "column": col_id},
        background="var(--gray-3)",
        border_radius="12px",
        padding="12px",
    )


def index() -> rx.Component:
    return rx.container(
        rx.color_mode.button(position="top-right"),
        # Monitor has no DOM footprint; it routes every drop to the state handler.
        dnd.monitor(on_drop=KanbanState.handle_drop),
        rx.vstack(
            rx.heading("reflex-pragmatic-drag-and-drop", size="7"),
            rx.text("Drag cards within and across columns.", color="var(--gray-11)"),
            rx.cond(
                KanbanState.last_event != "",
                rx.callout(KanbanState.last_event, icon="info", size="1"),
            ),
            rx.hstack(
                *[column(c) for c in COLUMNS],
                spacing="4",
                align="start",
            ),
            spacing="4",
            padding_y="2em",
        ),
        max_width="900px",
    )


app = rx.App()
app.add_page(index)
