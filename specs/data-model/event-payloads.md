# reflex-pragmatic-dnd — Data Model Specification

## Metadata

| Campo | Valor |
|---|---|
| **Autor** | Ernesto (ecrespo) |
| **Estado** | `DRAFT` |
| **Versión** | 1.0 |
| **Fecha** | 2026-06-14 |
| **Almacenamiento** | En memoria (`rx.State`) — sin base de datos |
| **Tech Design Relacionado** | ../technical/architecture.md |

---

## 1. Visión General del Modelo

Esta librería no persiste datos: el "modelo de datos" son (a) los **payloads de
evento** que cruzan el WebSocket cliente→servidor y (b) el **estado de aplicación**
que el desarrollador mantiene en `rx.State`. Todos los payloads son JSON.

```
Draggable ──(getInitialData)──▶ source        ┐
DropTarget ─(getData+hitbox)──▶ target/edge   ├─▶ Monitor.onDrop ─▶ rx.State (Python)
                                              ┘
```

## 2. Estructuras de Payload

### 2.1 `SourceData` (datos del ítem arrastrado)

Construido por `Draggable.getInitialData`. Forma base + lo que el usuario pase en `item_data`.

```json
{
  "dragId": "string (== drag_id del componente)",
  "...itemData": "claves arbitrarias provistas por el usuario"
}
```

| Campo | Tipo | Origen | Notas |
|---|---|---|---|
| `dragId` | string | `drag_id` | Requerido, estable. |
| `*` (extra) | JSON | `item_data` | Pequeño y serializable. |

### 2.2 `TargetData` (datos del objetivo de soltado)

Construido por `DropTarget.getData`; si `with_closest_edge`, incluye el símbolo de
borde (extraído como string en los payloads).

```json
{
  "dropId": "string (== drop_id)",
  "...targetData": "claves arbitrarias provistas por el usuario",
  "closestEdge": "top | bottom | left | right | null"
}
```

### 2.3 Payload de `Monitor.on_drop`

```json
{
  "source": { "dragId": "c1", "cardId": "c1" },
  "dropTargets": [
    { "dropId": "c4", "kind": "card", "cardId": "c4", "closestEdge": "bottom" },
    { "dropId": "doing", "kind": "column", "column": "doing" }
  ],
  "target": { "dropId": "c4", "kind": "card", "cardId": "c4", "closestEdge": "bottom" }
}
```

| Campo | Tipo | Descripción |
|---|---|---|
| `source` | object | `SourceData` del ítem arrastrado. |
| `dropTargets` | array | Objetivos atravesados, **del más interno al más externo**. |
| `target` | object\|null | `dropTargets[0]` por conveniencia. |

### 2.4 Payload de `DropTarget.on_drop` / `on_drag_enter`

```json
{ "dropId": "z", "closestEdge": "top|null", "source": { }, "target": { } }
```

## 3. Estado de Aplicación de Referencia (demo Kanban)

Definido por el usuario en `rx.State` (no por la librería). Documentado aquí para
mostrar el patrón de consumo.

```python
cards: dict[str, list[dict]] = {
    "todo":  [{"id": "c1", "title": "..."}],
    "doing": [{"id": "c4", "title": "..."}],
    "done":  [{"id": "c5", "title": "..."}],
}
```

| Entidad | Forma | Relación |
|---|---|---|
| `Column` | clave string (`todo`/`doing`/`done`) | 1:N con `Card` |
| `Card` | `{ "id": str, "title": str }` | pertenece a una columna |

### Invariantes
- `Card.id` único en todo el board (necesario para `drag_id`).
- El orden dentro de cada lista **es** el orden visual (índice = posición).
- Las mutaciones reasignan `self.cards` (Reflex detecta cambios por reasignación, no por mutación in-place).

## 4. Reglas de Transformación (handle_drop)

```
entrada: payload (sección 2.3)
1. source.cardId requerido y dropTargets no vacío, si no → no-op.
2. to_col = (col_target ?? card_target).column ; debe existir en COLUMNS.
3. Reconstruir board inmutable; extraer la card por id.
4. Si card_target y card_target.cardId != source.cardId:
     idx = posición de card_target.cardId
     si closestEdge == "bottom": idx += 1
     insertar en idx
   si no: append al final de to_col.
5. self.cards = board   # reasignación → reactividad
```

## 5. Consideraciones de Serialización

- El cliente aplica `JSON.parse(JSON.stringify(...))` (`clean()`); cualquier valor no
  serializable (funciones, símbolos, referencias circulares) se descarta.
- El borde más cercano es un `Symbol` en Pragmatic; se exporta como `string` para
  poder cruzar el socket.
- Mantener `item_data`/`target_data` pequeños (ids y metadatos), no objetos pesados.
