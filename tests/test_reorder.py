"""Tests for the pure reorder helpers.

These encode the transformation rules from the SDD artifacts:
  - data-model/event-payloads.md §4 (handle_drop rules)
  - api/component-api-v1.md §4 (edge cases)

The helpers are pure functions: (state, payload) -> new state. They never
mutate their inputs and return the original object unchanged on a no-op.
"""

from __future__ import annotations

import pytest

from reflex_pragmatic_dnd.reorder import move_card, reorder_list

COLUMNS = ["todo", "doing", "done"]


def board() -> dict[str, list[dict]]:
    """A fresh reference board (matches data-model §3)."""
    return {
        "todo": [
            {"id": "c1", "title": "one"},
            {"id": "c2", "title": "two"},
            {"id": "c3", "title": "three"},
        ],
        "doing": [{"id": "c4", "title": "four"}],
        "done": [{"id": "c5", "title": "five"}],
    }


def monitor_payload(source, drop_targets):
    """Shape produced by Monitor.on_drop (data-model §2.3)."""
    return {
        "source": source,
        "dropTargets": drop_targets,
        "target": drop_targets[0] if drop_targets else None,
    }


# --------------------------------------------------------------------------- #
# move_card — Kanban board reducer (data-model §4)
# --------------------------------------------------------------------------- #


def test_move_card_to_another_column_appends_at_end():
    payload = monitor_payload(
        {"cardId": "c1"},
        [{"kind": "column", "column": "doing"}],
    )
    result = move_card(board(), payload, columns=COLUMNS)
    assert [c["id"] for c in result["doing"]] == ["c4", "c1"]
    assert [c["id"] for c in result["todo"]] == ["c2", "c3"]


def test_reorder_within_column_before_card_with_top_edge():
    # Drop c3 above c1 (closest edge top) -> c3 goes before c1.
    payload = monitor_payload(
        {"cardId": "c3"},
        [
            {"kind": "card", "cardId": "c1", "closestEdge": "top"},
            {"kind": "column", "column": "todo"},
        ],
    )
    result = move_card(board(), payload, columns=COLUMNS)
    assert [c["id"] for c in result["todo"]] == ["c3", "c1", "c2"]


def test_reorder_within_column_after_card_with_bottom_edge():
    # Drop c1 below c2 (closest edge bottom) -> c1 goes after c2.
    payload = monitor_payload(
        {"cardId": "c1"},
        [
            {"kind": "card", "cardId": "c2", "closestEdge": "bottom"},
            {"kind": "column", "column": "todo"},
        ],
    )
    result = move_card(board(), payload, columns=COLUMNS)
    assert [c["id"] for c in result["todo"]] == ["c2", "c1", "c3"]


def test_move_card_across_columns_relative_to_card():
    # Drop c4 (doing) above c2 in todo.
    payload = monitor_payload(
        {"cardId": "c4"},
        [
            {"kind": "card", "cardId": "c2", "closestEdge": "top"},
            {"kind": "column", "column": "todo"},
        ],
    )
    result = move_card(board(), payload, columns=COLUMNS)
    assert [c["id"] for c in result["todo"]] == ["c1", "c4", "c2", "c3"]
    assert result["doing"] == []


def test_drop_outside_any_target_is_noop():
    # API §4: dropTargets == [] -> handler ignores.
    original = board()
    payload = monitor_payload({"cardId": "c1"}, [])
    result = move_card(original, payload, columns=COLUMNS)
    assert result == original


def test_drop_card_onto_itself_is_noop():
    # API §4: target.cardId == source.cardId -> no-op.
    original = board()
    payload = monitor_payload(
        {"cardId": "c1"},
        [
            {"kind": "card", "cardId": "c1", "closestEdge": "top"},
            {"kind": "column", "column": "todo"},
        ],
    )
    result = move_card(original, payload, columns=COLUMNS)
    assert result == original


def test_unknown_destination_column_is_noop():
    original = board()
    payload = monitor_payload(
        {"cardId": "c1"},
        [{"kind": "column", "column": "archive"}],
    )
    result = move_card(original, payload, columns=COLUMNS)
    assert result == original


def test_missing_source_id_is_noop():
    original = board()
    payload = monitor_payload({}, [{"kind": "column", "column": "doing"}])
    result = move_card(original, payload, columns=COLUMNS)
    assert result == original


def test_move_card_does_not_mutate_input():
    original = board()
    snapshot = {c: [dict(x) for x in original[c]] for c in COLUMNS}
    payload = monitor_payload(
        {"cardId": "c1"}, [{"kind": "column", "column": "doing"}]
    )
    move_card(original, payload, columns=COLUMNS)
    assert original == snapshot


def test_move_card_custom_id_key():
    # The drag payload may key its id under something other than "cardId".
    b = {"a": [{"id": "x1"}], "b": []}
    payload = monitor_payload(
        {"itemId": "x1"}, [{"kind": "column", "column": "b"}]
    )
    result = move_card(b, payload, columns=["a", "b"], id_key="itemId")
    assert [c["id"] for c in result["b"]] == ["x1"]
    assert result["a"] == []


# --------------------------------------------------------------------------- #
# reorder_list — single sortable list reducer (examples/sortable_list.py)
# --------------------------------------------------------------------------- #


def items() -> list[dict]:
    return [
        {"id": "a", "label": "Apple"},
        {"id": "b", "label": "Banana"},
        {"id": "c", "label": "Cherry"},
    ]


def test_reorder_list_before_target_top_edge():
    payload = monitor_payload(
        {"id": "c"}, [{"id": "a", "closestEdge": "top"}]
    )
    result = reorder_list(items(), payload)
    assert [x["id"] for x in result] == ["c", "a", "b"]


def test_reorder_list_after_target_bottom_edge():
    payload = monitor_payload(
        {"id": "a"}, [{"id": "b", "closestEdge": "bottom"}]
    )
    result = reorder_list(items(), payload)
    assert [x["id"] for x in result] == ["b", "a", "c"]


def test_reorder_list_onto_self_is_noop():
    original = items()
    payload = monitor_payload({"id": "a"}, [{"id": "a", "closestEdge": "top"}])
    result = reorder_list(original, payload)
    assert result == original


def test_reorder_list_empty_targets_is_noop():
    original = items()
    result = reorder_list(original, monitor_payload({"id": "a"}, []))
    assert result == original


def test_reorder_list_does_not_mutate_input():
    original = items()
    snapshot = [dict(x) for x in original]
    reorder_list(original, monitor_payload({"id": "a"}, [{"id": "c", "closestEdge": "bottom"}]))
    assert original == snapshot