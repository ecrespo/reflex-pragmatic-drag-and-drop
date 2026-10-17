// pragmatic_dnd.jsx
// React glue layer that bridges Atlassian's Pragmatic drag and drop (a low-level,
// framework-agnostic DnD toolchain) into Reflex-friendly React components.
//
// Reflex wraps each exported component below as a Python component. Event-handler
// props (onDragStart, onDrop, ...) are injected by Reflex and forwarded to the
// Python event handlers with a plain serialisable payload.
//
// Docs: https://atlassian.design/components/pragmatic-drag-and-drop/

import { useEffect, useRef, useState } from "react";

// Dedicated entry points (core >= 3.x, hitbox >= 2.1). The legacy
// `element/adapter`, `combine` and `closest-edge` barrels are deprecated.
import {
  draggable,
  dropTargetForElements,
  monitorForElements,
} from "@atlaskit/pragmatic-drag-and-drop/adapter/element-adapter";
import { combine } from "@atlaskit/pragmatic-drag-and-drop/utils/combine";
import { autoScrollForElements } from "@atlaskit/pragmatic-drag-and-drop-auto-scroll/element";
import { attachClosestEdge } from "@atlaskit/pragmatic-drag-and-drop-hitbox/closest-edge/attach-closest-edge";
import { extractClosestEdge } from "@atlaskit/pragmatic-drag-and-drop-hitbox/closest-edge/extract-closest-edge";
import { DropIndicator } from "@atlaskit/pragmatic-drag-and-drop-react-drop-indicator/box";

// Strip non-serialisable values so payloads can cross the Reflex websocket.
function clean(data) {
  try {
    return JSON.parse(JSON.stringify(data ?? {}));
  } catch (e) {
    return {};
  }
}

// ---------------------------------------------------------------------------
// Draggable: makes its child element draggable and carries `item_data`.
// ---------------------------------------------------------------------------
export function PdndDraggable({
  dragId,
  itemData,
  dragHandleSelector,
  onDragStart,
  onDrop,
  children,
  ...props
}) {
  const ref = useRef(null);
  const [dragging, setDragging] = useState(false);

  useEffect(() => {
    const element = ref.current;
    if (!element) return;
    const handle = dragHandleSelector
      ? element.querySelector(dragHandleSelector) ?? element
      : element;

    return draggable({
      element,
      dragHandle: handle,
      getInitialData: () => clean({ dragId, ...(itemData || {}) }),
      onDragStart: () => {
        setDragging(true);
        onDragStart && onDragStart(clean({ dragId, itemData }));
      },
      onDrop: () => {
        setDragging(false);
        onDrop && onDrop(clean({ dragId, itemData }));
      },
    });
  }, [dragId, dragHandleSelector, JSON.stringify(itemData)]);

  return (
    <div ref={ref} data-dragging={dragging} data-drag-id={dragId} {...props}>
      {children}
    </div>
  );
}

// ---------------------------------------------------------------------------
// DropTarget: registers a drop target. Supports closest-edge hitbox so callers
// can build sortable lists/boards, and reports the edge in the drop payload.
// ---------------------------------------------------------------------------
export function PdndDropTarget({
  dropId,
  targetData,
  withClosestEdge,
  allowedEdges,
  showDropIndicator,
  dropIndicatorGap,
  dropIndicatorType,
  dropIndicatorAppearance,
  onDragEnter,
  onDragLeave,
  onDrop,
  children,
  ...props
}) {
  const ref = useRef(null);
  const [closestEdge, setClosestEdge] = useState(null);
  const [isOver, setIsOver] = useState(false);

  useEffect(() => {
    const element = ref.current;
    if (!element) return;

    return dropTargetForElements({
      element,
      getData: ({ input, element: el }) => {
        const base = clean({ dropId, ...(targetData || {}) });
        if (withClosestEdge) {
          return attachClosestEdge(base, {
            input,
            element: el,
            allowedEdges: allowedEdges || ["top", "bottom"],
          });
        }
        return base;
      },
      onDragEnter: ({ self, source }) => {
        setIsOver(true);
        if (withClosestEdge) setClosestEdge(extractClosestEdge(self.data));
        onDragEnter &&
          onDragEnter(
            clean({
              dropId,
              closestEdge: withClosestEdge ? extractClosestEdge(self.data) : null,
              source: source.data,
            })
          );
      },
      onDrag: ({ self }) => {
        if (withClosestEdge) setClosestEdge(extractClosestEdge(self.data));
      },
      onDragLeave: () => {
        setIsOver(false);
        setClosestEdge(null);
        onDragLeave && onDragLeave(clean({ dropId }));
      },
      onDrop: ({ self, source }) => {
        const edge = withClosestEdge ? extractClosestEdge(self.data) : null;
        setIsOver(false);
        setClosestEdge(null);
        onDrop &&
          onDrop(
            clean({
              dropId,
              closestEdge: edge,
              source: source.data,
              target: edge ? { ...self.data, closestEdge: edge } : self.data,
            })
          );
      },
    });
  }, [
    dropId,
    withClosestEdge,
    JSON.stringify(targetData),
    JSON.stringify(allowedEdges),
  ]);

  // The indicator line is absolutely positioned against this wrapper, so it
  // needs a positioned ancestor. Callers can still override via `style`.
  const indicatorEnabled = showDropIndicator && withClosestEdge;
  const { style, ...rest } = props;
  const wrapperStyle = indicatorEnabled
    ? { position: "relative", ...(style || {}) }
    : style;

  return (
    <div
      ref={ref}
      data-over={isOver}
      data-closest-edge={closestEdge || ""}
      data-drop-id={dropId}
      style={wrapperStyle}
      {...rest}
    >
      {children}
      {indicatorEnabled && closestEdge && (
        <DropIndicator
          edge={closestEdge}
          gap={dropIndicatorGap}
          type={dropIndicatorType}
          appearance={dropIndicatorAppearance}
        />
      )}
    </div>
  );
}

// ---------------------------------------------------------------------------
// Monitor: invisible component that listens to all drag operations on the page
// and reports start/drop globally. Useful for a single state-update handler.
// ---------------------------------------------------------------------------
export function PdndMonitor({ onDragStart, onDrop, children }) {
  useEffect(() => {
    return monitorForElements({
      onDragStart: ({ source }) =>
        onDragStart && onDragStart(clean({ source: source.data })),
      onDrop: ({ source, location }) => {
        // `attachClosestEdge` stores the edge under a Symbol key, which
        // JSON serialisation drops; surface it as a plain `closestEdge` field.
        const targets = location.current.dropTargets.map((t) => {
          const edge = extractClosestEdge(t.data);
          return edge ? { ...t.data, closestEdge: edge } : t.data;
        });
        onDrop &&
          onDrop(
            clean({
              source: source.data,
              dropTargets: targets,
              // The innermost target is the most specific one.
              target: targets.length ? targets[0] : null,
            })
          );
      },
    });
  }, []);
  return <>{children || null}</>;
}

// ---------------------------------------------------------------------------
// AutoScrollContainer: enables auto-scrolling while dragging over this element.
// `maxScrollSpeed` ("standard" | "fast") and `allowedAxis` ("all" | "vertical" |
// "horizontal") map to the auto-scroll 3.x `getConfiguration`/`getAllowedAxis`.
// ---------------------------------------------------------------------------
export function PdndScrollContainer({
  maxScrollSpeed,
  allowedAxis,
  children,
  ...props
}) {
  const ref = useRef(null);
  useEffect(() => {
    const element = ref.current;
    if (!element) return;
    return combine(
      dropTargetForElements({ element }),
      autoScrollForElements({
        element,
        getConfiguration: () => ({ maxScrollSpeed: maxScrollSpeed || "standard" }),
        getAllowedAxis: () => allowedAxis || "all",
      })
    );
  }, [maxScrollSpeed, allowedAxis]);
  return (
    <div ref={ref} {...props}>
      {children}
    </div>
  );
}
