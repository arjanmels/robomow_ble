# Contributing

## Development setup

```bash
git clone https://github.com/arjanmels/robomow_ble.git
cd robomow_ble
python -m venv .venv
.venv\Scripts\activate  # Windows
pip install -e .[test,docs]
git config core.hooksPath .githooks
```

This repository includes a native Git `pre-commit` hook that:
- Regenerates API docs into `site/`
- Runs `pytest -q`
- Runs `ruff check .`
- Runs `pyright`

If you prefer one command for all required developer tooling:

```bash
pip install -e .[dev]
```

## Running tests

```bash
.venv\Scripts\activate  # Windows
pytest -q
```

## Release checklist

Before publishing a new release:

1. Bump `version` in `pyproject.toml`.
2. Update `CHANGELOG.md` with the release notes.
3. Run tests:

    ```bash
    pytest -q
    ```

4. Create a git tag and push it to trigger the release workflow:

    ```bash
    git tag v0.1.1
    git push origin v0.1.1
    ```

    This will automatically build, test, and publish to **TestPyPI**.

5. Once verified on TestPyPI, manually trigger the workflow to publish to **real PyPI**:

    - Go to Actions → Release workflow
    - Click "Run workflow"
    - Select "pypi" from the repository dropdown
    - Click "Run workflow"

The GitHub Actions workflow will automatically:
- Build and test the package
- Push tags (`v*`) to **TestPyPI** by default (safe testing environment)
- Allow manual trigger to publish to **real PyPI** (from Actions → Run workflow → select "pypi")

## Documentation

API documentation is generated from Python docstrings using [pdoc](https://pdoc.dev/) and published to GitHub Pages on every push to `main`.

- Published docs: https://arjanmels.github.io/robomow_ble/
- Source of truth: docstrings in `src/robomow_ble_lib/`

Generate docs locally:

```bash
.venv\Scripts\activate  # Windows
python -m pdoc --docformat google robomow_ble_lib -o site
```

Docs are rebuilt and deployed to GitHub Pages automatically on every push to `main`.
