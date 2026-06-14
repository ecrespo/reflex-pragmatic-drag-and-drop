"""Pure reducers for drag-and-drop payloads.

These helpers turn a ``Monitor.on_drop`` payload (see
``specs/data-model/event-payloads.md`` §2.3) into a new application state. They
are the Python side of the contract: deterministic, side-effect free, and easy
to unit test.

They are *optional* utilities — the library never forces a state shape on the
user — but the demo app and the sortable-list example both build on them so the
documented transformation rules (data-model §4) live in exactly one place.

Conventions:
  * Inputs are never mutated.
  * On a no-op (drop outside any target, drop onto self, unknown destination,
    missing ids) the original object is returned unchanged.
  * ``id_key`` is the key under which the dragged/target id travels inside the
    payload (``cardId`` for the Kanban demo, ``id`` for the list example).
"""

from __future__ import annotations


def move_card(
    board: dict[str, list[dict]],
    payload: dict,
    *,
    columns: list[str],
    id_key: str = "cardId",
    card_id_field: str = "id",
) -> dict[str, list[dict]]:
    """Move/reorder a card across columns from a Monitor drop payload.

    Implements data-model §4. ``board`` maps column id -> ordered list of card
    dicts. Each card is identified within the board by ``card_id_field`` and in
    the payload by ``id_key``.
    """
    payload = payload or {}
    source = payload.get("source") or {}
    targets = payload.get("dropTargets") or []

    card_id = source.get(id_key)
    if not card_id or not targets:
        return board

    card_target = next((t for t in targets if t.get("kind") == "card"), None)
    col_target = next((t for t in targets if t.get("kind") == "column"), None)

    to_col = (col_target or card_target or {}).get("column")
    if to_col not in columns:
        return board

    # API §4: dropping a card onto itself is a no-op.
    if card_target and card_target.get(id_key) == card_id:
        return board

    # Rebuild immutably so callers can reassign and trigger Reflex reactivity.
    new_board = {c: [dict(x) for x in board[c]] for c in columns}

    moving = None
    for col in columns:
        for i, item in enumerate(new_board[col]):
            if item.get(card_id_field) == card_id:
                moving = new_board[col].pop(i)
                break
        if moving is not None:
            break
    if moving is None:
        return board

    dest = new_board[to_col]
    if card_target is not None:
        idx = next(
            (
                i
                for i, x in enumerate(dest)
                if x.get(card_id_field) == card_target.get(id_key)
            ),
            len(dest),
        )
        if card_target.get("closestEdge") == "bottom":
            idx += 1
        dest.insert(idx, moving)
    else:
        dest.append(moving)

    return new_board


def reorder_list(
    items: list[dict],
    payload: dict,
    *,
    id_key: str = "id",
) -> list[dict]:
    """Reorder a single flat list from a Monitor drop payload.

    Used by the sortable-list example. ``dropTargets[0]`` is the hovered item;
    ``closestEdge`` decides whether the moved item lands before or after it.
    """
    payload = payload or {}
    source = payload.get("source") or {}
    targets = payload.get("dropTargets") or []

    sid = source.get(id_key)
    if not sid or not targets:
        return items

    target = targets[0]
    tid = target.get(id_key)
    if not tid or tid == sid:
        return items

    moving = next((x for x in items if x.get(id_key) == sid), None)
    if moving is None:
        return items

    new_items = [dict(x) for x in items if x.get(id_key) != sid]
    idx = next(
        (i for i, x in enumerate(new_items) if x.get(id_key) == tid),
        len(new_items),
    )
    if target.get("closestEdge") == "bottom":
        idx += 1
    new_items.insert(idx, dict(moving))
    return new_items
