"""Conformance tests for the component wrappers.

Encodes the component contract from api/component-api-v1.md §2 and the technical
decisions from technical/architecture.md (NoSSR, bundled glue, pinned deps).
These run at the Reflex component layer — no browser required.
"""

from __future__ import annotations

import reflex as rx
from reflex.components.component import NoSSRComponent

import reflex_pragmatic_dnd as dnd


# --------------------------------------------------------------------------- #
# Public API surface (api §1)
# --------------------------------------------------------------------------- #


def test_public_api_exports():
    for name in [
        "Draggable",
        "DropTarget",
        "Monitor",
        "ScrollContainer",
        "draggable",
        "drop_target",
        "monitor",
        "scroll_container",
        "move_card",
        "reorder_list",
    ]:
        assert hasattr(dnd, name), f"missing public export: {name}"


def test_factories_build_their_component_class():
    assert isinstance(dnd.draggable(drag_id="a"), dnd.Draggable)
    assert isinstance(dnd.drop_target(drop_id="z"), dnd.DropTarget)
    assert isinstance(dnd.monitor(), dnd.Monitor)
    assert isinstance(dnd.scroll_container(), dnd.ScrollContainer)


# --------------------------------------------------------------------------- #
# Tags map to the JSX glue exports (tech design §3.2)
# --------------------------------------------------------------------------- #


def test_component_tags():
    assert dnd.draggable(drag_id="a").tag == "PdndDraggable"
    assert dnd.drop_target(drop_id="z").tag == "PdndDropTarget"
    assert dnd.monitor().tag == "PdndMonitor"
    assert dnd.scroll_container().tag == "PdndScrollContainer"


# --------------------------------------------------------------------------- #
# DD-002: every wrapper is client-only (NoSSR)
# --------------------------------------------------------------------------- #


def test_all_components_are_nossr():
    assert isinstance(dnd.draggable(drag_id="a"), NoSSRComponent)
    assert isinstance(dnd.drop_target(drop_id="z"), NoSSRComponent)
    assert isinstance(dnd.monitor(), NoSSRComponent)
    assert isinstance(dnd.scroll_container(), NoSSRComponent)


# --------------------------------------------------------------------------- #
# DD-001: glue bundled locally + the full @atlaskit suite pinned (PRD obj 4.1)
# --------------------------------------------------------------------------- #


def test_glue_bundled_as_local_asset():
    lib = dnd.draggable(drag_id="a").library
    assert "pragmatic_dnd.jsx" in lib


def test_full_atlaskit_suite_is_declared_and_pinned():
    deps = dnd.draggable(drag_id="a").lib_dependencies
    suite = {
        "@atlaskit/pragmatic-drag-and-drop",
        "@atlaskit/pragmatic-drag-and-drop-hitbox",
        "@atlaskit/pragmatic-drag-and-drop-auto-scroll",
        "@atlaskit/pragmatic-drag-and-drop-react-drop-indicator",
    }
    declared = {d.split("@", 1)[0] if not d.startswith("@") else "@" + d[1:].split("@")[0] for d in deps}
    assert suite <= declared
    # Every dependency must be version-pinned (carry an "@<range>" suffix).
    for d in deps:
        name_and_version = d.rsplit("@", 1)
        assert len(name_and_version) == 2 and name_and_version[1], f"unpinned dep: {d}"


# --------------------------------------------------------------------------- #
# Props are snake_case in Python and camelCase in the rendered React (api §3)
# --------------------------------------------------------------------------- #


def test_draggable_props_render_as_camel_case():
    rendered = str(dnd.draggable(rx.text("x"), drag_id="a", item_data={"cardId": "a"}).render())
    assert "dragId" in rendered
    assert "itemData" in rendered


def test_drop_target_props_render_as_camel_case():
    rendered = str(
        dnd.drop_target(
            rx.text("x"),
            drop_id="z",
            target_data={"kind": "zone"},
            with_closest_edge=True,
            allowed_edges=["top", "bottom"],
        ).render()
    )
    assert "dropId" in rendered
    assert "withClosestEdge" in rendered
    assert "allowedEdges" in rendered


# --------------------------------------------------------------------------- #
# Event handlers exist as documented (api §2)
# --------------------------------------------------------------------------- #


def test_draggable_event_triggers():
    triggers = dnd.draggable(drag_id="a").get_event_triggers()
    assert "on_drag_start" in triggers
    assert "on_drop" in triggers


def test_drop_target_event_triggers():
    triggers = dnd.drop_target(drop_id="z").get_event_triggers()
    assert {"on_drag_enter", "on_drag_leave", "on_drop"} <= set(triggers)


def test_monitor_event_triggers():
    triggers = dnd.monitor().get_event_triggers()
    assert {"on_drag_start", "on_drop"} <= set(triggers)


def test_components_render_without_error():
    # Building a representative tree (api §5) must not raise at the Reflex layer.
    tree = rx.box(
        dnd.monitor(),
        dnd.draggable(rx.text("drag me"), drag_id="a", item_data={"cardId": "a"}),
        dnd.drop_target(rx.text("drop here"), drop_id="z", target_data={"kind": "zone"}),
        dnd.scroll_container(rx.text("scroll")),
    )
    assert tree.render() is not None
