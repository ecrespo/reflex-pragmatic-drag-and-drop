"""Demo app: a sortable Kanban board built with reflex_pragmatic_dnd.

Showcases the Pragmatic drag and drop 4.x suite: closest-edge reordering with
the Atlaskit ``DropIndicator`` line, drag handles, and auto-scrolling columns
with a configurable ``max_scroll_speed``.

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
            {"id": "c6", "title": "Pin the @atlaskit suite"},
            {"id": "c7", "title": "Write the reorder reducers"},
            {"id": "c8", "title": "Cover reducers with tests"},
            {"id": "c9", "title": "Publish v0.1.1"},
            {"id": "c10", "title": "Bump to pragmatic-dnd 4.x"},
            {"id": "c11", "title": "Migrate to new entry points"},
        ],
    }
    last_event: str = ""
    # Demo controls for the 4.x features.
    show_indicator: bool = True
    scroll_speed: str = "standard"

    @rx.event
    def set_show_indicator(self, value: bool):
        self.show_indicator = value

    @rx.event
    def set_scroll_speed(self, value: str | list[str]):
        # The segmented control is single-select, so `value` is always a str.
        self.scroll_speed = value if isinstance(value, str) else value[0]

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
    """A sortable card: the drop target draws the edge indicator, the
    draggable inside only starts a drag from its grip handle."""
    return dnd.drop_target(
        dnd.draggable(
            rx.hstack(
                rx.icon(
                    "grip-vertical",
                    size=16,
                    class_name="drag-handle",
                    cursor="grab",
                    color="var(--gray-9)",
                    flex_shrink="0",
                ),
                rx.text(item["title"], size="2"),
                align="center",
                spacing="2",
            ),
            drag_id=item["id"],
            item_data={"cardId": item["id"]},
            drag_handle_selector=".drag-handle",
            background="var(--gray-2)",
            border="1px solid var(--gray-5)",
            border_radius="8px",
            padding="10px",
            _hover={"border_color": "var(--accent-8)"},
            # Fade the source card while it is being dragged.
            style={"&[data-dragging='true']": {"opacity": "0.4"}},
        ),
        drop_id=item["id"],
        target_data={"kind": "card", "cardId": item["id"]},
        with_closest_edge=True,
        allowed_edges=["top", "bottom"],
        show_drop_indicator=KanbanState.show_indicator,
        # Matches the vertical spacing between cards so the line sits between them.
        drop_indicator_gap="8px",
    )


def column(col_id: str) -> rx.Component:
    """A column is a drop target (append) whose card list auto-scrolls."""
    return dnd.drop_target(
        rx.vstack(
            rx.hstack(
                rx.heading(COLUMN_TITLES[col_id], size="3"),
                rx.badge(KanbanState.cards[col_id].length(), variant="soft"),
                justify="between",
                width="100%",
            ),
            dnd.scroll_container(
                rx.vstack(
                    rx.foreach(KanbanState.cards[col_id], card),
                    rx.box(height="20px"),  # bottom drop zone padding
                    align="stretch",
                    spacing="2",
                ),
                max_scroll_speed=KanbanState.scroll_speed,
                allowed_axis="vertical",
                max_height="300px",
                overflow_y="auto",
                padding_x="2px",
            ),
            align="stretch",
            width="260px",
            min_height="340px",
        ),
        drop_id=col_id,
        target_data={"kind": "column", "column": col_id},
        background="var(--gray-3)",
        border_radius="12px",
        padding="12px",
    )


def controls() -> rx.Component:
    """Toggles for the features added with the pragmatic-dnd 4.x upgrade."""
    return rx.hstack(
        rx.hstack(
            rx.switch(
                checked=KanbanState.show_indicator,
                on_change=KanbanState.set_show_indicator,
            ),
            rx.text("Drop indicator", size="2"),
            align="center",
        ),
        rx.hstack(
            rx.text("Auto-scroll speed", size="2"),
            rx.segmented_control.root(
                rx.segmented_control.item("Standard", value="standard"),
                rx.segmented_control.item("Fast", value="fast"),
                value=KanbanState.scroll_speed,
                on_change=KanbanState.set_scroll_speed,
                size="1",
            ),
            align="center",
        ),
        spacing="6",
        wrap="wrap",
    )


def index() -> rx.Component:
    return rx.container(
        rx.color_mode.button(position="top-right"),
        # Monitor has no DOM footprint; it routes every drop to the state handler.
        dnd.monitor(on_drop=KanbanState.handle_drop),
        rx.vstack(
            rx.heading("reflex-pragmatic-drag-and-drop", size="7"),
            rx.text(
                "Drag cards by their grip within and across columns. "
                "Hover near a column's edge to auto-scroll.",
                color="var(--gray-11)",
            ),
            controls(),
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
