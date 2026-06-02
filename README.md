# Robomow-BLE

`robomow_ble` is a standalone Python library for talking to Robomow mowers over
Bluetooth Low Energy (BLE).

It provides a reusable BLE protocol layer for Robomow mowers and can be used
directly in Python applications.

## Current status

- Developed in this repository.
- Not published to PyPI yet.
- Requires Python 3.12+.

## Installation

Until this package is published, install it from source:

```bash
pip install -e .[test]
```

## Main API

Top-level exports from `robomow_ble`:

- `RobomowDevice`: main BLE client and control API.
- `RobomowUpdate`: update callback payload (`key`, `value`).
- `EntityKey`: enum of update/state keys.
- `WireSignalType`: enum for wire signal settings.
- `RobomowAuthenticationError`: raised when BLE authentication fails.

### `RobomowDevice`

Create a device instance with:

- `address`: BLE MAC address.
- `mainboard_serial`: mower mainboard serial (used during auth).
- `update_callback`: optional callback called with `RobomowUpdate` when values
	change.

Important methods:

- Connection lifecycle:
	- `async_connect(device)`
	- `async_disconnect()`
	- `is_connected()`
- Common controls:
	- `async_start_mowing(duration_minutes=None, starting_zone=None)`
	- `async_start_mowing_edge()`
	- `async_stop_mowing()`
	- `async_return_to_home()`
- Settings:
	- `async_enable_schedule()` / `async_disable_schedule()`
	- `async_set_schedule(schedule)`
	- `async_enable_anti_theft()` / `async_disable_anti_theft()`
	- `async_enable_child_lock()` / `async_disable_child_lock()`
	- `async_set_wire_signal_type(wire_signal_type)`
	- `async_set_starting_point_a(value)` / `async_set_starting_point_b(value)`

Common read-only state properties include:

- Identity/version: `family`, `model`, `mainboard_version`,
	`software_version`, `software_release`
- Live state: `operating_state`, `message`, `battery_level`, `rssi`
- Schedule/status: `schedule_enabled`, `schedule`, `next_departure`,
	`previous_departure`, `expected_duration`, `no_depart_reason`
- Safety/system flags: `anti_theft_enabled`, `anti_theft_active`,
	`child_lock_enabled`, `mower_home`, `charging_active`

## Minimal example

```python
import asyncio

from bleak import BleakScanner
from robomow_ble import EntityKey, RobomowDevice, RobomowUpdate


def on_update(update: RobomowUpdate) -> None:
    if update.key == EntityKey.BATTERY_LEVEL:
        print(f"Battery: {update.value}%")
    else:
        print(f"{update.key}: {update.value}")


async def main() -> None:
    # Replace these with your mower details
    address = "AA:BB:CC:DD:EE:FF"
    mainboard_serial = "12345678901234"

    ble_device = await BleakScanner.find_device_by_address(address, timeout=15.0)
    if ble_device is None:
        raise RuntimeError("Mower not found")

    mower = RobomowDevice(
        address=address,
        mainboard_serial=mainboard_serial,
        update_callback=on_update,
    )

    await mower.async_connect(ble_device)
    try:
        await mower.async_start_mowing(duration_minutes=30)
        await asyncio.sleep(5)
        print("State:", mower.operating_state)
    finally:
        await mower.async_disconnect()


if __name__ == "__main__":
    asyncio.run(main())
```

## Release checklist

Before publishing a new release to PyPI:

1. Bump `version` in `pyproject.toml`.
2. Update `CHANGELOG.md` with the release notes.
3. Run tests:

    ```bash
    pip install -e .[test]
    pytest -q
    ```

4. Build distributions:

    ```bash
    python -m pip install build twine
    python -m build
    ```

5. Validate package metadata and README rendering:

    ```bash
    python -m twine check dist/*
    ```

6. Create a git tag such as `v0.1.1` and push it to trigger the release workflow.

7. If you want a manual fallback, you can still upload with Twine after a local build.

