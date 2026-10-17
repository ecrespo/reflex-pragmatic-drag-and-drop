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
unzip -l dist/reflex_pragmatic_drag_and_drop-0.2.0-py3-none-any.whl
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

## Automated release (GitHub Actions)

Two workflows live in `.github/workflows/`:

| Workflow | Trigger | What it does |
|---|---|---|
| `ci.yml` | PR / push to `develop` and `main` | `uv sync --locked` + `pytest` on Python 3.12 and 3.13. |
| `publish.yml` | tag `v*`, or manual run | Runs CI → checks tag == `pyproject` == `__version__` → `uv build` → verifies the `.jsx` is in the wheel → `twine check --strict` → uploads to PyPI → creates a GitHub release with the dists attached. |

Uploads use **PyPI Trusted Publishing** (OIDC), so no API token is stored in
GitHub.

### One-time setup

1. On PyPI: *Your projects → reflex-pragmatic-drag-and-drop → Manage → Publishing →
   Add a new publisher (GitHub)* with:
   - Owner: `ecrespo` · Repository: `reflex-pragmatic-drag-and-drop`
   - Workflow name: `publish.yml` · Environment name: `pypi`
2. (Optional, for dry runs) the same on <https://test.pypi.org> with environment
   name `testpypi`. TestPyPI is a separate account/project.
3. On GitHub: *Settings → Environments* → create `pypi` (and `testpypi`). For
   extra safety add yourself as a *required reviewer* on `pypi` and restrict it
   to tags `v*`.

### Cutting a release

```bash
# on develop: bump the version in pyproject.toml and reflex_pragmatic_dnd/__init__.py
uv version 0.2.1 && sed -i 's/__version__ = ".*"/__version__ = "0.2.1"/' reflex_pragmatic_dnd/__init__.py
uv lock && uv run pytest
git commit -am "release: v0.2.1"
# PR develop -> main, merge, then tag main:
git switch main && git pull
git tag -a v0.2.1 -m "v0.2.1" && git push origin v0.2.1
```

The tag push starts `publish.yml`; if the tag does not match the package
version the build fails before anything is uploaded. To try the pipeline without
touching PyPI, run *Actions → Publish → Run workflow* with `testpypi`.

## Releasing a new version manually

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
