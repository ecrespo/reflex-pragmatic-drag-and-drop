# reflex-pragmatic-dnd — Component API Specification

## Metadata

| Campo | Valor |
|---|---|
| **Autor** | Ernesto (ecrespo) |
| **Estado** | `DRAFT` |
| **Versión API** | v1.0 |
| **Fecha** | 2026-06-14 |
| **PRD Relacionado** | ../prd/reflex-pragmatic-dnd.md |

---

## 1. Visión General

El "API" de esta librería es su **superficie de componentes Python**: las clases y
factorías que el desarrollador importa desde `reflex_pragmatic_dnd`, sus props y
sus manejadores de eventos. Hace las veces de contrato entre la librería y la app
del usuario. No hay API HTTP.

Importación:

```python
import reflex_pragmatic_dnd as dnd
# dnd.draggable, dnd.drop_target, dnd.monitor, dnd.scroll_container
```

## 2. Componentes

### 2.1 `draggable(*children, **props)` → `Draggable`

Envuelve `@atlaskit/pragmatic-drag-and-drop/element/adapter#draggable`.

| Prop | Tipo Python | Requerido | Descripción |
|---|---|---|---|
| `drag_id` | `str` | Sí | Identificador estable del ítem; viaja en cada evento. |
| `item_data` | `dict` | No | Payload arbitrario JSON-serializable adjunto al arrastre. |
| `drag_handle_selector` | `str` | No | Selector CSS interno usado como "agarre"; por defecto, todo el elemento. |

**Eventos**

| Evento | Payload | Cuándo |
|---|---|---|
| `on_drag_start` | `{ "dragId": str, "itemData": dict }` | Comienza el arrastre. |
| `on_drop` | `{ "dragId": str, "itemData": dict }` | Termina (soltado o cancelado). |

### 2.2 `drop_target(*children, **props)` → `DropTarget`

Envuelve `dropTargetForElements` + (opcional) `@atlaskit/pragmatic-drag-and-drop-hitbox/closest-edge`.

| Prop | Tipo Python | Requerido | Descripción |
|---|---|---|---|
| `drop_id` | `str` | Sí | Identificador del objetivo. |
| `target_data` | `dict` | No | Datos del objetivo, incluidos en el payload de soltado. |
| `with_closest_edge` | `bool` | No (def. `False`) | Activa el hitbox de borde más cercano. |
| `allowed_edges` | `list[str]` | No (def. `["top","bottom"]`) | Bordes considerados: `top`/`bottom`/`left`/`right`. |

**Eventos**

| Evento | Payload | Cuándo |
|---|---|---|
| `on_drag_enter` | `{ "dropId", "closestEdge"\|null, "source": dict }` | El puntero entra al objetivo. |
| `on_drag_leave` | `{ "dropId" }` | El puntero sale. |
| `on_drop` | `{ "dropId", "closestEdge"\|null, "source": dict, "target": dict }` | Se suelta sobre el objetivo. |

**Atributos del DOM expuestos para estilizar (CSS):**
`data-over="true|false"`, `data-closest-edge="top|bottom|..."`, `data-drop-id`.

### 2.3 `monitor(**props)` → `Monitor`

Envuelve `monitorForElements`. No renderiza huella visible.

**Eventos**

| Evento | Payload | Cuándo |
|---|---|---|
| `on_drag_start` | `{ "source": dict }` | Cualquier arrastre en la página comienza. |
| `on_drop` | `{ "source": dict, "dropTargets": list[dict], "target": dict\|null }` | Cualquier arrastre termina. `dropTargets[0]` es el objetivo más interno. |

### 2.4 `scroll_container(*children, **props)` → `ScrollContainer`

Envuelve `combine(dropTargetForElements, autoScrollForElements)`. Hace auto-scroll
mientras se arrastra cerca de los bordes del contenedor. Sin eventos propios en v1.0.

## 3. Convenciones

- **Serialización:** el *glue* aplica `JSON.parse(JSON.stringify(...))` a todo
  payload antes de enviarlo a Python; valores no serializables se descartan.
- **Nombres:** props en `snake_case` (Python) ↔ props React en `camelCase` (mapeo
  automático de Reflex). Las claves *dentro* de los payloads usan `camelCase`
  (`dragId`, `closestEdge`) por venir del lado JS.
- **Identificadores:** `drag_id`/`drop_id` deben ser únicos y estables entre
  renders para que el reordenamiento sea correcto.

## 4. Errores y Casos Borde

| Caso | Comportamiento esperado |
|---|---|
| Soltar fuera de cualquier `DropTarget` | `Monitor.on_drop` con `dropTargets == []`; el handler debe ignorar. |
| `item_data` con objetos no serializables | Se descartan silenciosamente (sanitización en cliente). |
| Soltar un ítem sobre sí mismo | `target.cardId == source.cardId`; el handler debe no-op. |
| Componente renderizado en SSR | Evitado: las clases son `NoSSRComponent` (import dinámico). |

## 5. Ejemplo mínimo (contrato en uso)

```python
import reflex as rx
import reflex_pragmatic_dnd as dnd

class S(rx.State):
    msg: str = ""
    @rx.event
    def on_drop(self, payload: dict):
        self.msg = f"{payload['source']} -> {payload.get('target')}"

def page():
    return rx.box(
        dnd.monitor(on_drop=S.on_drop),
        dnd.draggable(rx.text("Arrástrame"), drag_id="a", item_data={"cardId": "a"}),
        dnd.drop_target(rx.text("Suéltalo aquí"), drop_id="z",
                        target_data={"kind": "zone"}),
        rx.text(S.msg),
    )
```
