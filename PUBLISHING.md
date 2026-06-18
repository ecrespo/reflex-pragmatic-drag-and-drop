# Publishing `reflex-pragmatic-drag-and-drop` to PyPI

This package is a **Reflex custom component**: a pip-installable Python package
that exposes Reflex `Component` wrappers (`reflex_pragmatic_dnd`) plus their
bundled React glue (`pragmatic_dnd.jsx`) and pinned `@atlaskit` npm dependencies.

The package manager for this repo is [`uv`](https://docs.astral.sh/uv/). The
Reflex CLI builds the component (`uv run reflex component build`); Reflex does not
upload to PyPI itself, so publishing is done with `uv publish` (or `twine`), and
`uv run reflex component share` registers the package in the Reflex gallery.

## Prerequisites for publishing

Per the [Reflex prerequisites guide](https://reflex.dev/docs/custom-components/prerequisites-for-publishing/),
make sure the following are in place. They already are in this repo unless noted:

- [x] **PyPI-friendly name** — `reflex-pragmatic-drag-and-drop` (the `reflex-`
      prefix makes it discoverable on PyPI). See `pyproject.toml` `[project].name`.
- [x] **`reflex-custom-components` keyword** — required for the component to show
      up in Reflex's component gallery (it searches PyPI for this keyword).
      See `[project].keywords`.
- [x] **`README.md`** — install + usage instructions, shipped as the PyPI long
      description (`readme = "README.md"`).
- [x] **`LICENSE`** — MIT, declared via `license` / `license-files`.
- [x] **Version, description, authors, classifiers, project URLs** — all set in
      `pyproject.toml`.
- [x] **Build backend** — `hatchling`; the wheel force-includes the `.jsx` glue
      (`[tool.hatch.build.targets.wheel].artifacts`).
- [ ] **A PyPI account** — register at <https://pypi.org/account/register/>.
- [ ] **An API token** — create one under *Account settings → API tokens* and use
      it as the password (username `__token__`). Store it in `~/.pypirc`,
      `UV_PUBLISH_TOKEN`, or pass `--token`.

## Build

Produce the source distribution (`.tar.gz`) and wheel (`.whl`) in `dist/`:

```bash
uv run reflex component build
```

Verify the wheel contains the package **and** the bundled glue:

```bash
unzip -l dist/reflex_pragmatic_drag_and_drop-0.1.1-py3-none-any.whl
# expect: reflex_pragmatic_dnd/{__init__,core,reorder}.py and pragmatic_dnd.jsx
```

> Tip: clean stale artifacts first with `rm -f dist/*.whl dist/*.tar.gz` so you
> only upload the current version.

## Publish

Reflex has no `component publish` command — it delegates uploading to standard
tooling. Upload everything in `dist/` to PyPI with `uv` (username is `__token__`,
password is your API token):

```bash
# Token via environment variable (recommended for CI):
UV_PUBLISH_TOKEN=pypi-XXXX uv publish

# or pass it explicitly:
uv publish --token pypi-XXXX
```

Test against TestPyPI first if you want a dry run:

```bash
uv publish --publish-url https://test.pypi.org/legacy/ --token pypi-XXXX
```

`twine upload dist/*` works as an equivalent (the `twine` dev dependency is
included for this).

## Register in the Reflex gallery (optional)

After publishing, add extra details so the component shows up in Reflex's
component gallery:

```bash
uv run reflex component share
```

## Verify the published package

In a throwaway environment:

```bash
uv pip install reflex-pragmatic-drag-and-drop
python -c "import reflex_pragmatic_dnd as dnd; print(dnd.__version__)"
```

## Releasing a new version

1. Bump the version in **both** places so they stay in sync:
   - `pyproject.toml` → `[project].version`
   - `reflex_pragmatic_dnd/__init__.py` → `__version__`
2. `uv run pytest` — the suite must pass.
3. `rm -f dist/*.whl dist/*.tar.gz && uv run reflex component build`
4. `uv publish`
5. Tag the release: `git tag v<version> && git push --tags`.

## `reflex component` command reference

See the
[command reference](https://reflex.dev/docs/custom-components/command-reference/).
The subcommands available in this Reflex version are:

| Command | Purpose |
|---|---|
| `uv run reflex component init` | Scaffold a new custom component project (already done here). |
| `uv run reflex component build` | Build `.tar.gz` + `.whl` into `dist/` (also regenerates `core.pyi`). |
| `uv run reflex component install` | Install this local component in editable mode for development. |
| `uv run reflex component share` | Register the published package in the Reflex gallery. |
| `uv publish` / `twine upload dist/*` | Upload `dist/` to PyPI (needs an account + token). |
