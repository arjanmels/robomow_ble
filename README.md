# Robomow-BLE

Robomow-BLE is a standalone Python library for talking to Robomow mowers over
Bluetooth Low Energy (BLE).

It provides a reusable BLE protocol layer for Robomow mowers and can be used
directly in Python applications.

Currently it only supports RT models. 
Support for other models may be added in the future if there is demand and access to devices for testing.

## API Overview

Please refer to the [API documentation](https://arjanmels.github.io/robomow_ble/) for details.

## How to use

### Install

Install from PyPI:

```bash
python -m pip install Robomow-BLE
```

### Create a device client

Create a `RobomowDevice` with:

- `mainboard_serial`: mower mainboard serial used during authentication.
- `update_callback` (optional): called for each update as `RobomowUpdate(key, value)`.


```python
from robomow_ble import RobomowDevice

mower = RobomowDevice(
    mainboard_serial="12345678901234",
)
```

### How to find `mainboard_serial`:

1. Log in to myrobomow.robomow.com.
2. Open your browser's Developer Tools (F12).
3. Go to the Network tab.
4. Reload the page.
5. Look for a request ending in `/api/customer/products`.
6. Click the request and open the Response tab.
7. In the JSON response, find the field named `MainboardSerial`. This value is the actual mainboard serial number.


### Connect and authenticate

Discover a BLE device with Bleak, then connect:

```python
from bleak import BleakScanner

ble_device = await BleakScanner.find_device_by_address(address, timeout=15.0)
if ble_device is None:
    raise RuntimeError("Mower not found")

await mower.async_connect(ble_device)
```

### Receive updates

Pass a callback to receive state changes:

```python
from robomow_ble import RobomowUpdate, EntityKey


def on_update(update: RobomowUpdate) -> None:
    if update.key == EntityKey.BATTERY_LEVEL:
        print(f"Battery: {update.value}%")
    else:
        print(f"{update.key}: {update.value}")
```

### Send commands

Common control methods:

- `await mower.async_start_mowing(duration_minutes=30)`
- `await mower.async_start_mowing_edge()`
- `await mower.async_stop_mowing()`
- `await mower.async_return_to_home()`

Common settings methods:

- `await mower.async_enable_schedule()` / `await mower.async_disable_schedule()`
- `await mower.async_set_schedule(schedule)`
- `await mower.async_enable_anti_theft()` / `await mower.async_disable_anti_theft()`
- `await mower.async_enable_child_lock()` / `await mower.async_disable_child_lock()`
- `await mower.async_set_wire_signal_type(wire_signal_type)`

### Read state

Example state properties:

- Identity/version: `family`, `model`, `mainboard_version`, `software_version`
- Live values: `operating_state`, `message`, `battery_level`, `rssi`
- Status: `schedule_enabled`, `next_departure`, `expected_duration`

### Disconnect cleanly

Always disconnect in a `finally` block:

```python
try:
    ...
finally:
    await mower.async_disconnect()
```

## Minimal example

```python
import asyncio

from bleak import BleakScanner
from robomow_ble import RobomowDevice, RobomowUpdate, EntityKey


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


