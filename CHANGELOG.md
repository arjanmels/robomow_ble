# Changelog

All notable changes to the RoboMow-BLE project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]


## [1.3.1] - 2026-06-22

- Fixed `next_departure` handling for invalid minute values (0xFFFF) by returning `None` and adding a week if it wraps around.
- Removed unnecessary `asyncio.CancelledError` suppression in disconnect logic.


## [1.3.0] - 2026-06-16

- `next_departure` is now exposed as a UTC `datetime` instead of a raw integer value.
- Renamed entity key/property `previous_departure` to `previous_duration` to reflect actual payload semantics.
- `no_depart_reason` now returns a structured `Message` object instead of a string.
- Improved RT state parsing by deriving `next_departure` from protocol minute offsets.
- Removed `mower_home` and `charging_active` device properties from the public state surface.
- Fixed state and error messages.

## [1.2.0] - 2026-06-14

- Fixed date/time sync.
- Fixed command counter wrap-around
- Added write lock to prevent disconnect during write.

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

[Unreleased]: https://github.com/arjanmels/robomow_ble/compare/v1.3.1...HEAD
[1.3.1]: https://github.com/arjanmels/robomow_ble/compare/v1.3.0...v1.3.1
[1.3.0]: https://github.com/arjanmels/robomow_ble/compare/v1.2.0...v1.3.0
[1.2.0]: https://github.com/arjanmels/robomow_ble/compare/v1.1.0...v1.2.0
[1.1.0]: https://github.com/arjanmels/robomow_ble/compare/v1.0.0...v1.1.0
[1.0.0]: https://github.com/arjanmels/robomow_ble/compare/v0.3.0...v1.0.0
[0.3.0]: https://github.com/arjanmels/robomow_ble/compare/v0.2.0...v0.3.0
[0.2.0]: https://github.com/arjanmels/robomow_ble/releases/tag/v0.2.0

