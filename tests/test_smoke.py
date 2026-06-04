"""Smoke tests for the robomow_ble package."""

from robomow_ble import (
    EntityKey,
    RobomowAuthenticationError,
    RobomowDevice,
    RobomowUpdate,
    WireSignalType,
)
from robomow_ble.const import MowerFamily, MowerModel


def test_top_level_exports_are_importable() -> None:
    """Public package exports should be importable."""
    assert EntityKey.BATTERY_LEVEL.value == "battery_level"
    assert WireSignalType.TYPE_A.value == 0
    assert RobomowAuthenticationError("x")


def test_update_named_tuple_shape() -> None:
    """RobomowUpdate should expose key and value fields."""
    update = RobomowUpdate(EntityKey.BATTERY_LEVEL, 86)

    assert update.key == EntityKey.BATTERY_LEVEL
    assert update.value == 86


def test_device_defaults_without_connection() -> None:
    """A fresh device should expose safe default values."""
    mower = RobomowDevice(
        mainboard_serial="12345678901234",
        update_callback=None,
    )

    assert mower.mainboard_serial == "12345678901234"
    assert mower.family == MowerFamily.Unknown
    assert mower.model == MowerModel.Unknown
    assert mower.is_connected() is False
