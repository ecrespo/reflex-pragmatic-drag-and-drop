# Specs — reflex-pragmatic-drag-and-drop

Documentación **Spec-Driven Design (SDD)**. Orden de lectura:

```
PRD (qué) → API Spec (contrato) → Tech Design (cómo) → Data Model → Implementation Plan
```

| Documento | Archivo |
|---|---|
| PRD | [prd/reflex-pragmatic-dnd.md](prd/reflex-pragmatic-dnd.md) |
| Component API Spec | [api/component-api-v1.md](api/component-api-v1.md) |
| Technical Design | [technical/architecture.md](technical/architecture.md) |
| Data Model (payloads) | [data-model/event-payloads.md](data-model/event-payloads.md) |
| Implementation Plan | [plans/implementation-plan.md](plans/implementation-plan.md) |

## Validación de coherencia
- Todos los requisitos del PRD (RF-001..004) están cubiertos por el API Spec (§2).
- Todos los campos del API Spec aparecen en el Data Model (§2).
- El Implementation Plan referencia los 4 documentos y cubre 5 fases.
