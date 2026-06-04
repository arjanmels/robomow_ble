"""Robomow-BLE provides a reusable Bluetooth Low Energy protocol layer for
communicating with Robomow mowers.

The package exposes a small top-level API intended for direct use:

- ``RobomowDevice``: main client used to connect, read state, and send commands.
- ``RobomowUpdate``: callback payload for state changes.
- ``RobomowAuthenticationError`` and ``RobomowProtocolError``: protocol errors.
- Enums: ``MowerFamily``, ``MowerModel``, ``MowerOperatingState``,
  ``EntityKey``, ``WireSignalType``, ``Zone``.
- Datatypes: ``MowerSchedule``, ``MowerSchedule.Day``, ``MowerOperation``,
  ``Message``.
"""

from .const import (
    EntityKey,
    Message,
    MowerFamily,
    MowerModel,
    MowerOperation,
    MowerOperatingState,
    MowerSchedule,
    WireSignalType,
    Zone,
)
from .exceptions import RobomowAuthenticationError, RobomowProtocolError
from .mower import RobomowDevice, RobomowUpdate

__all__ = [
    "RobomowDevice",
    "RobomowUpdate",
    "RobomowProtocolError",
    "RobomowAuthenticationError",
    "Message",
    "MowerOperation",
    "MowerFamily",
    "MowerModel",
    "MowerSchedule",
    "MowerOperatingState",
    "EntityKey",
    "WireSignalType",
    "Zone",
]
