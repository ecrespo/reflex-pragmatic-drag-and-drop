# Changelog

## 0.3.0

- **Requires Reflex ≥ 0.10** (was ≥ 0.9.5.post2). The lockfiles (`uv.lock`,
  `reflex.lock/`) were refreshed against Reflex 0.10.0.
- Demo app: `RadixThemesPlugin` is now declared explicitly in `rxconfig.py`
  (implicit Radix Themes enablement is deprecated and goes away in Reflex 1.0).
- Tests: the demo-state tests run the demo app in its own `RegistrationContext`,
  since Reflex 0.10 allows a single `rx.App` per context.
- Docs: build with `uv build` instead of `reflex component build` — Reflex 0.10
  removed the `reflex component` CLI.
- CI: workflows force the Node 24 runtime for JavaScript actions, the CI sets up
  Node 24 and compiles the demo app; `astral-sh/setup-uv` bumped to v10.3.2.

## 0.2.1

- CI and PyPI publish workflows (Trusted Publishing).

## 0.2.0

- Pragmatic drag and drop 4.x pins, Atlaskit drop indicator, auto-scroll
  config and a `closestEdge` fix.
