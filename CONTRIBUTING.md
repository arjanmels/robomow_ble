# Contributing

## Development setup

```bash
git clone https://github.com/arjanmels/robomow_ble.git
cd robomow_ble
python -m venv .venv
.venv\Scripts\activate  # Windows
pip install -e .[test,docs]
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

The GitHub Actions workflow will build, test, and publish to TestPyPI automatically.

## Documentation

API documentation is generated from Python docstrings using [pdoc](https://pdoc.dev/) and published to GitHub Pages on every push to `main`.

- Published docs: https://arjanmels.github.io/robomow_ble/
- Source of truth: docstrings in `src/robomow_ble/`

Generate docs locally:

```bash
.venv\Scripts\activate  # Windows
python -m pdoc --docformat google robomow_ble -o site
```

Docs are rebuilt and deployed to GitHub Pages automatically on every push to `main`.
