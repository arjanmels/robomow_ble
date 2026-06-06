# Changelog

All notable changes to the RoboMow-BLE project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

## [1.1.0] - 2026-06-06

- Renamed Python package module from `robomow_ble` to `robomow_ble_lib`.
- Added repository pre-commit hook to regenerate docs and run tests, Ruff, and Pyright.
- Added GitHub Actions lint workflow for tests, Ruff, and Pyright.
- Added `dev` optional dependency group for local CI/lint tooling.
- Improved Pyright compatibility for dataclass-based models.

## [1.0.0] - 2026-06-04

- Added dual PyPI/TestPyPI publishing with manual selection.
- Added `CONTRIBUTING.md` guide.
- Fixed GitHub Actions Node.js 24 compatibility.

## [0.3.0] - 2026-06-04

- Added API documentation workflow and GitHub Pages deployment.
- Added docs-only enum representation via `ROBOMOW_BLE_DOCS` environment variable.

## [0.2.0] - 2026-06-04

- Improved public API and docstrings.
- Expanded README with full usage guide and examples.

## 0.1.0 - 2026-06-02

- Initial release of the Robomow BLE protocol library.

[Unreleased]: https://github.com/arjanmels/robomow_ble/compare/v1.1.0...HEAD
[1.1.0]: https://github.com/arjanmels/robomow_ble/compare/v1.0.0...v1.1.0
[1.0.0]: https://github.com/arjanmels/robomow_ble/compare/v0.3.0...v1.0.0
[0.3.0]: https://github.com/arjanmels/robomow_ble/compare/v0.2.0...v0.3.0
[0.2.0]: https://github.com/arjanmels/robomow_ble/releases/tag/v0.2.0

