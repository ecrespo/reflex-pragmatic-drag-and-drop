"""Integration tests for the demo app and example states.

These exercise the actual Reflex ``rx.State`` event handlers (which delegate to
the pure reducers) to prove the wiring works end-to-end. Reflex forbids direct
state instantiation, so we use the internal init flag and call the raw handler
function via ``EventHandler.fn``.
"""

from __future__ import annotations

from examples.sortable_list import ListState
from reflex_pragmatic_drag_and_drop.reflex_pragmatic_drag_and_drop import (
    COLUMNS,
    KanbanState,
)


def make(state_cls):
    return state_cls(_reflex_internal_init=True)


def col_ids(state, col):
    return [c["id"] for c in state.cards[col]]


def test_kanban_move_card_across_columns():
    s = make(KanbanState)
    KanbanState.handle_drop.fn(
        s,
        {"source": {"cardId": "c1"}, "dropTargets": [{"kind": "column", "column": "doing"}]},
    )
    assert col_ids(s, "doing") == ["c4", "c1"]
    assert "Doing" in s.last_event


def test_kanban_reorder_within_column():
    s = make(KanbanState)
    KanbanState.handle_drop.fn(
        s,
        {
            "source": {"cardId": "c1"},
            "dropTargets": [
                {"kind": "card", "cardId": "c2", "closestEdge": "bottom"},
                {"kind": "column", "column": "todo"},
            ],
        },
    )
    assert col_ids(s, "todo") == ["c2", "c1", "c3"]


def test_kanban_drop_outside_target_is_noop():
    s = make(KanbanState)
    before = {c: col_ids(s, c) for c in COLUMNS}
    KanbanState.handle_drop.fn(s, {"source": {"cardId": "c1"}, "dropTargets": []})
    after = {c: col_ids(s, c) for c in COLUMNS}
    assert before == after


def test_kanban_drop_onto_self_is_noop():
    s = make(KanbanState)
    before = {c: col_ids(s, c) for c in COLUMNS}
    KanbanState.handle_drop.fn(
        s,
        {
            "source": {"cardId": "c1"},
            "dropTargets": [
                {"kind": "card", "cardId": "c1", "closestEdge": "top"},
                {"kind": "column", "column": "todo"},
            ],
        },
    )
    after = {c: col_ids(s, c) for c in COLUMNS}
    assert before == after


def test_list_reorder():
    s = make(ListState)
    ListState.reorder.fn(
        s,
        {"source": {"id": "a"}, "dropTargets": [{"id": "c", "closestEdge": "bottom"}]},
    )
    # Example list is [a, b, c, d]; moving a after c -> [b, c, a, d].
    assert [x["id"] for x in s.items] == ["b", "c", "a", "d"]


def test_list_reorder_onto_self_is_noop():
    s = make(ListState)
    before = [x["id"] for x in s.items]
    ListState.reorder.fn(
        s,
        {"source": {"id": "a"}, "dropTargets": [{"id": "a", "closestEdge": "top"}]},
    )
    assert [x["id"] for x in s.items] == before