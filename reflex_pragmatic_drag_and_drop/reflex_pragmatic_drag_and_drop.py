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
        """Global drop handler fed by the Monitor component."""
        source = payload.get("source") or {}
        targets = payload.get("dropTargets") or []
        card_id = source.get("cardId")
        if not card_id or not targets:
            return

        card_target = next((t for t in targets if t.get("kind") == "card"), None)
        col_target = next((t for t in targets if t.get("kind") == "column"), None)
        # The column drop target carries the destination column id.
        to_col = (col_target or card_target or {}).get("column")
        if to_col not in COLUMNS:
            return

        # Rebuild the board immutably so Reflex detects the change.
        board = {c: [dict(x) for x in self.cards[c]] for c in COLUMNS}
        moving = None
        for col in COLUMNS:
            for i, item in enumerate(board[col]):
                if item["id"] == card_id:
                    moving = board[col].pop(i)
                    break
            if moving:
                break
        if not moving:
            return

        dest = board[to_col]
        if card_target and card_target.get("cardId") != card_id:
            # Reorder relative to the hovered card using the closest edge.
            idx = next(
                (i for i, x in enumerate(dest) if x["id"] == card_target["cardId"]),
                len(dest),
            )
            if card_target.get("closestEdge") == "bottom":
                idx += 1
            dest.insert(idx, moving)
        else:
            dest.append(moving)

        self.cards = board
        self.last_event = f"Moved '{moving['title']}' -> {COLUMN_TITLES[to_col]}"


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
