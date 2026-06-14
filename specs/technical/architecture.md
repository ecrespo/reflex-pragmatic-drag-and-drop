# reflex-pragmatic-dnd — Technical Design Document

## Metadata

| Campo | Valor |
|---|---|
| **Autor** | Ernesto (ecrespo) |
| **Estado** | `DRAFT` |
| **Versión** | 1.0 |
| **Fecha** | 2026-06-14 |
| **PRD Relacionado** | ../prd/reflex-pragmatic-dnd.md |
| **API Spec Relacionado** | ../api/component-api-v1.md |

---

## 1. Contexto

Reflex compila componentes Python a React y sirve un backend FastAPI; el estado
vive en Python y se sincroniza por WebSocket. Pragmatic drag and drop, en cambio,
es imperativo: se *adjunta* a un `HTMLElement` (`draggable({element, ...})`) y
devuelve una función de limpieza. El reto técnico es tender un puente entre el
modelo declarativo de Reflex y el modelo imperativo basado en refs/efectos de
Pragmatic, manteniendo los payloads serializables para cruzar el WebSocket.

La estrategia elegida es un **glue de React local** (`pragmatic_dnd.jsx`) empaquetado
con la librería mediante `rx.asset`, y un conjunto de **wrappers Python**
(`NoSSRComponent`) que exponen props y `EventHandler`.

## 2. Objetivos Técnicos

- **Correctitud:** cada efecto registra y limpia su suscripción (`return cleanup`) para no fugar listeners entre renders.
- **Rendimiento:** el JS de Atlassian corre nativo en el cliente; Reflex solo recibe eventos discretos (start/drop), no el movimiento continuo.
- **Mantenibilidad:** un único archivo de glue + wrappers delgados; versiones npm pineadas.
- **Portabilidad:** sin dependencia de SSR; serialización defensiva de payloads.

## 3. Arquitectura Propuesta

### 3.1 Diagrama de Alto Nivel

```
┌─────────────────────────────┐      compila a       ┌──────────────────────────────┐
│  App Reflex (Python)         │  ───────────────▶    │  Frontend React (.web)        │
│  - rx.State (cards, ...)     │                      │  - PdndDraggable / PdndDrop…  │
│  - dnd.draggable/drop_target │                      │    (pragmatic_dnd.jsx)        │
│  - handle_drop(@rx.event)    │   ◀── WebSocket ───  │  - useEffect + draggable()/   │
└─────────────────────────────┘   evento on_drop      │    dropTargetForElements()/   │
                                   (payload JSON)      │    monitorForElements()       │
                                                       └───────────────┬───────────────┘
                                                                       │ usa
                                                       ┌───────────────▼───────────────┐
                                                       │ @atlaskit/pragmatic-drag-and-  │
                                                       │ drop (+ hitbox, auto-scroll,   │
                                                       │ react-drop-indicator)          │
                                                       └────────────────────────────────┘
```

### 3.2 Componentes

| Componente | Tecnología | Responsabilidad |
|---|---|---|
| `pragmatic_dnd.jsx` | React (JSX) | Adjuntar Pragmatic a elementos vía `useEffect`/`useRef`; normalizar y emitir payloads. |
| `core.py` | Reflex `NoSSRComponent` | Exponer `Draggable`/`DropTarget`/`Monitor`/`ScrollContainer` con props y eventos. |
| `__init__.py` | Python | API pública y factorías (`draggable`, …). |
| `lib_dependencies` | npm | Instalar `@atlaskit/pragmatic-drag-and-drop*` en `.web`. |
| App demo | Reflex | Kanban ordenable que consume la librería. |

### 3.3 Flujo de Datos

**Flujo: soltar una tarjeta en otra columna**

```
1. El usuario inicia el arrastre de una tarjeta (PdndDraggable).
2. El glue llama draggable({getInitialData: () => {dragId, ...itemData}}).
3. Al entrar a un DropTarget con hitbox, attachClosestEdge calcula el borde.
4. Al soltar, monitorForElements.onDrop reúne {source, dropTargets}.
5. El glue sanitiza el payload (JSON) y llama onDrop(payload).
6. Reflex envía el evento por WebSocket a KanbanState.handle_drop.
7. El handler reconstruye el board de forma inmutable y reasigna self.cards.
8. Reflex difunde el nuevo estado y el frontend re-renderiza.
```

**Flujo de error / borde:**

```
1. Soltar fuera de todo target → dropTargets == [] → handler hace no-op.
2. Datos no serializables → descartados por clean() antes de cruzar el socket.
3. Render duplicado → cleanup del useEffect anterior evita listeners colgados.
```

## 4. Decisiones de Diseño

### DD-001: Glue JSX local vs. paquete npm propio
- **Decisión:** empaquetar `pragmatic_dnd.jsx` con `rx.asset(shared=True)` y declarar
  las dependencias `@atlaskit` vía `lib_dependencies`.
- **Alternativas:** (a) publicar un paquete npm propio que reexporte; (b) inyectar
  todo con `add_hooks` (hooks crudos en cada wrapper).
- **Razón:** el asset local evita una cadena de publicación npm y mantiene el glue
  versionado junto al Python; `add_hooks` crudo es más frágil y difícil de leer.

### DD-002: `NoSSRComponent`
- **Decisión:** todas las clases heredan de `NoSSRComponent`.
- **Razón:** Pragmatic usa `document`/`window`; el import dinámico evita fallos de SSR.

### DD-003: Eventos discretos, no streaming del movimiento
- **Decisión:** solo cruzan el WebSocket eventos `start`/`enter`/`leave`/`drop`.
- **Razón:** el cálculo continuo (posición, borde) ocurre en el cliente; enviar cada
  `onDrag` saturaría el socket. El estado de Python solo cambia al soltar.

### DD-004: Monitor como fuente única de verdad para boards
- **Decisión:** recomendar un único `monitor(on_drop=...)` por board en lugar de un
  handler por tarjeta.
- **Razón:** simplifica la lógica de recolocación y reduce props por ítem.

## 5. Estructura del Repositorio

```
reflex-pragmatic-drag-and-drop/
├── reflex_pragmatic_dnd/            # LIBRERÍA
│   ├── __init__.py                  # API pública
│   ├── core.py                      # wrappers NoSSRComponent
│   └── pragmatic_dnd.jsx            # glue React (rx.asset)
├── reflex_pragmatic_drag_and_drop/  # APP DEMO (Kanban)
│   └── reflex_pragmatic_drag_and_drop.py
├── examples/                        # ejemplos adicionales (lista ordenable)
├── specs/                           # esta documentación SDD
├── rxconfig.py
└── pyproject.toml
```

## 6. Riesgos y Mitigaciones

| Riesgo | Impacto | Mitigación |
|---|---|---|
| Cambios de API en `@atlaskit` | Roturas al actualizar | Versiones pineadas (`^1.x`), pruebas de humo del build. |
| Reflex cambia el patrón de assets | Glue no carga | Cubrir con CI sobre la versión de Reflex soportada. |
| Payloads grandes | Latencia | `item_data` debe ser pequeño; documentado en el API Spec. |
| Reordenamiento incorrecto con ids inestables | UX rota | Requisito explícito de `drag_id`/`drop_id` estables. |
