# reflex-pragmatic-drag-and-drop

## Product Requirements Document (PRD)

| Campo | Valor |
|---|---|
| **Autor** | Ernesto (ecrespo) |
| **Estado** | `DRAFT` |
| **Versión** | 1.0 |
| **Fecha** | 2026-06-14 |
| **Reviewers** | — |
| **Última actualización** | 2026-06-14 |

---

## 1. Resumen Ejecutivo

`reflex-pragmatic-drag-and-drop` es una librería de componentes para [Reflex](https://reflex.dev)
que expone, en Python puro, las capacidades de [Pragmatic drag and drop](https://github.com/atlassian/pragmatic-drag-and-drop)
de Atlassian: un *toolchain* de arrastrar-y-soltar de bajo nivel, agnóstico del framework,
construido sobre la API nativa de drag and drop del navegador.

El objetivo es que un desarrollador de Reflex pueda construir experiencias de
drag and drop (listas ordenables, tableros Kanban, reordenamiento de árboles,
auto-scroll) **sin escribir JavaScript**, usando componentes y manejadores de
eventos idiomáticos de Reflex. La librería envuelve la familia completa de
paquetes `@atlaskit/pragmatic-drag-and-drop-*` (core, hitbox, auto-scroll,
react-drop-indicator).

## 2. Contexto y Problema

### 2.1 Situación Actual
Reflex no incluye primitivas de drag and drop. Quien las necesita debe envolver
manualmente una librería JS de React (HTML5 DnD, dnd-kit, react-dnd…) siguiendo
el flujo de "Wrapping React", lo cual exige conocimiento de React, hooks y del
sistema de assets de Reflex.

### 2.2 Problema
Pragmatic drag and drop es hoy una de las mejores opciones (rendimiento, peso,
accesibilidad, independencia del framework) pero su API está pensada para
imperativamente adjuntar comportamiento a elementos del DOM vía `useEffect` y
funciones de limpieza. Trasladar ese modelo a Reflex (estado en Python,
renderizado declarativo) no es trivial y se reimplementa una y otra vez.

### 2.3 Oportunidad
Empaquetar una sola vez el *glue* React→Reflex y publicarlo como librería
reutilizable: API estable en Python, eventos serializables, y ejemplos listos
para copiar (Kanban, lista ordenable).

## 3. Usuarios Objetivo

### Persona 1: Desarrollador Reflex de producto
- **Descripción:** construye dashboards y herramientas internas con Reflex.
- **Necesidad principal:** tableros y listas reordenables sin tocar JS.
- **Frecuencia de uso:** recurrente durante el desarrollo de features.
- **Nivel técnico:** medio (Python alto, JS bajo).

### Persona 2: Mantenedor de librerías de componentes Reflex
- **Descripción:** publica componentes para la comunidad Reflex.
- **Necesidad principal:** un patrón de referencia para envolver librerías JS
  basadas en refs/efectos y exponerlas con eventos tipados.
- **Nivel técnico:** alto.

## 4. Objetivos y Métricas de Éxito

### 4.1 Objetivos del Producto

| Objetivo | Métrica | Target | Plazo |
|---|---|---|---|
| Cubrir la suite completa | Paquetes `@atlaskit` envueltos | 4/4 (core, hitbox, auto-scroll, drop-indicator) | v1.0 |
| Onboarding rápido | Tiempo a primer board funcional | < 15 min copiando el ejemplo | v1.0 |
| Cero JS para el usuario | Líneas de JS en el app del usuario | 0 | v1.0 |

### 4.2 Objetivos de Usuario

| Objetivo del Usuario | Indicador |
|---|---|
| Crear una lista ordenable | API `draggable` + `drop_target(with_closest_edge=True)` |
| Mover ítems entre contenedores | Un único `monitor(on_drop=...)` |
| Scroll automático en listas largas | `scroll_container` |

## 5. Alcance

### 5.1 In Scope (Incluido)
- [x] Componente `Draggable` (registra un elemento como arrastrable, con `item_data`).
- [x] Componente `DropTarget` (objetivo de soltado, con hitbox de borde más cercano).
- [x] Componente `Monitor` (escucha global de operaciones de drag).
- [x] Componente `ScrollContainer` (auto-scroll durante el arrastre).
- [x] Eventos: `on_drag_start`, `on_drop`, `on_drag_enter`, `on_drag_leave`.
- [x] Empaquetado del *glue* JSX vía `rx.asset` + dependencias npm declaradas.
- [x] Ejemplo Kanban ordenable y ejemplo de lista.

### 5.2 Out of Scope (Excluido)
- Adaptadores de texto y de archivos externos (`text/adapter`, external) — futura iteración.
- Indicadores de soltado avanzados con `react-drop-indicator` *estilizados* (se expone el borde; el render del indicador queda a cargo del usuario en v1.0).
- Soporte de teclado / accesibilidad avanzada más allá de lo que provee el core.
- Persistencia del estado (responsabilidad de la app del usuario).

### 5.3 Futuras Consideraciones
- Componente `DropIndicator` estilizado envolviendo `@atlaskit/...-react-drop-indicator`.
- Adaptador externo (arrastrar archivos/URLs desde fuera del navegador).
- Publicación en PyPI como `reflex-pragmatic-dnd` y registro de componentes Reflex.

## 6. Requisitos Funcionales

### RF-001: Declarar un elemento arrastrable
- **Descripción:** el sistema debe permitir marcar cualquier subárbol de componentes como arrastrable y adjuntarle datos.
- **Actor:** desarrollador.
- **Precondiciones:** componente montado en cliente (NoSSR).
- **Flujo principal:** `draggable(child, drag_id=..., item_data={...})` → al iniciar/terminar el arrastre se emiten `on_drag_start`/`on_drop` con el payload.
- **Criterio de aceptación:** el handler de Python recibe `dragId` e `item_data`.

### RF-002: Declarar un objetivo de soltado con borde
- **Descripción:** registrar un drop target que, opcionalmente, reporte el borde más cercano (top/bottom/left/right) para reordenar.
- **Criterio de aceptación:** `on_drop` incluye `closestEdge`, `source` y `target`.

### RF-003: Escucha global con Monitor
- **Descripción:** un único componente sin huella en el DOM que reporta `source` y la pila de `dropTargets` de cada operación.
- **Criterio de aceptación:** un solo handler puede recolocar un ítem en cualquier columna.

### RF-004: Auto-scroll
- **Descripción:** contenedor que hace scroll automático cuando se arrastra cerca de sus bordes.
- **Criterio de aceptación:** listas más altas que el viewport hacen scroll durante el arrastre.

## 7. Requisitos No Funcionales
- **RNF-01 (Compatibilidad):** Reflex ≥ 0.9, Python ≥ 3.12.
- **RNF-02 (Cero JS de usuario):** toda la lógica JS vive en el *glue* empaquetado.
- **RNF-03 (Serializable):** todo payload de evento debe ser JSON-serializable (se sanitiza en el cliente).
- **RNF-04 (SSR-safe):** los componentes son `NoSSRComponent` (usan `document`).
