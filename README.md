# reflex-pragmatic-drag-and-drop

Bindings de [Reflex](https://reflex.dev) para
[Pragmatic drag and drop](https://github.com/atlassian/pragmatic-drag-and-drop)
de Atlassian. Construye listas ordenables y tableros Kanban en **Python puro**,
sin escribir JavaScript.

Envuelve la suite completa: `@atlaskit/pragmatic-drag-and-drop` (core),
`-hitbox` (borde más cercano), `-auto-scroll` y `-react-drop-indicator`.

## Estado

Núcleo funcional (Fases 1–3 del plan). Ver [`specs/`](specs/) para el diseño
completo (PRD, API, Tech Design, Data Model, Plan).

## Requisitos

- Python ≥ 3.12 · Reflex ≥ 0.9 · gestor de paquetes [`uv`](https://docs.astral.sh/uv/)

## Instalación y ejecución (demo Kanban)

```bash
uv sync                 # instala dependencias Python
uv run reflex run       # instala paquetes @atlaskit en .web y arranca en :3000
```

Abre http://localhost:3000 y arrastra las tarjetas entre columnas.

## Uso

```python
import reflex as rx
import reflex_pragmatic_dnd as dnd


class State(rx.State):
    msg: str = ""

    @rx.event
    def on_drop(self, payload: dict):
        self.msg = f"{payload['source']} -> {payload.get('target')}"


def index():
    return rx.box(
        # Escucha global: un único handler para toda la página.
        dnd.monitor(on_drop=State.on_drop),

        # Un elemento arrastrable que lleva datos.
        dnd.draggable(
            rx.text("Arrástrame"),
            drag_id="card-1",
            item_data={"cardId": "card-1"},
        ),

        # Un objetivo de soltado con detección de borde (para reordenar).
        dnd.drop_target(
            rx.text("Suéltalo aquí"),
            drop_id="zone-1",
            target_data={"kind": "zone"},
            with_closest_edge=True,
            allowed_edges=["top", "bottom"],
        ),

        rx.text(State.msg),
    )
```

### Componentes

| Factoría | Envuelve | Eventos |
|---|---|---|
| `dnd.draggable(...)` | `draggable` (element adapter) | `on_drag_start`, `on_drop` |
| `dnd.drop_target(...)` | `dropTargetForElements` (+ hitbox) | `on_drag_enter`, `on_drag_leave`, `on_drop` |
| `dnd.monitor(...)` | `monitorForElements` | `on_drag_start`, `on_drop` |
| `dnd.scroll_container(...)` | `autoScrollForElements` | — |

Detalle completo de props y payloads: [`specs/api/component-api-v1.md`](specs/api/component-api-v1.md).

## Ejemplos

- **Kanban ordenable:** [`reflex_pragmatic_drag_and_drop/reflex_pragmatic_drag_and_drop.py`](reflex_pragmatic_drag_and_drop/reflex_pragmatic_drag_and_drop.py) (app por defecto).
- **Lista ordenable:** [`examples/sortable_list.py`](examples/sortable_list.py).

## Estructura

```
reflex_pragmatic_dnd/            # la librería (wrappers + glue JSX)
reflex_pragmatic_drag_and_drop/  # app demo Kanban
examples/                        # ejemplos adicionales
specs/                           # documentación SDD
```

## Cómo funciona

Un *glue* React local (`pragmatic_dnd.jsx`, empaquetado con `rx.asset`) adjunta
Pragmatic a los elementos del DOM mediante `useEffect`/`useRef` y emite payloads
JSON-serializables. Wrappers `NoSSRComponent` los exponen como componentes Reflex
con eventos tipados. Solo cruzan el WebSocket eventos discretos (start/drop); el
cálculo continuo ocurre en el cliente. Ver
[`specs/technical/architecture.md`](specs/technical/architecture.md).

## Licencia

MIT.
