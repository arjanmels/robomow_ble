"""Shared constants and enums for the Robomow BLE package."""

from __future__ import annotations

import datetime
import logging
from enum import IntEnum, StrEnum

from attr import dataclass, field

LOGGER: logging.Logger = logging.getLogger(__package__)

MAINBOARD_SERIAL_LENGTH = 14
AUTH_RESPONSE_LENGTH = 15

MINIMUM_MESSAGE_LENGTH = 4
MESSAGE_START_BYTE = 0xAA
MESSAGE_SEND_BYTE = 0x1F
MESSAGE_RECEIVE_BYTE = 0x1E

UUID_SERVICE = "ff00a501-d020-913c-1234-56d97200a6a6"
UUID_CHAR_AUTHENTICATE = "ff00a502-d020-913c-1234-56d97200a6a6"
UUID_CHAR_DATA_OUT = "ff00a503-d020-913c-1234-56d97200a6a6"
UUID_CHAR_DATA_IN = "ff00a506-d020-913c-1234-56d97200a6a6"

UNKNOWN_FIELD_VALUE = 0xFFFF


class MessageType(IntEnum):
    """Basic message types used in packet payloads."""

    ACKNOWLEDGE = 0x04
    CLEAR_USER_MESSAGE = 0x0E
    GET_CONFIG = 0x0F
    COMMAND = 0x15
    MISCELLANEOUS = 0x16
    GET_MESSAGE = 0x1B
    UPDATE_DATE_TIME = 0x1D
    WRITE_EEPROM = 0x1F
    READ_EEPROM = 0x20


class WireSignalType(IntEnum):
    """Wire signal types used in EEPROM parameters."""

    TYPE_A = 0x00
    TYPE_B = 0x01
    TYPE_C = 0x02


class Zone(IntEnum):
    """Robomow mower zones."""

    MAIN = 0
    STARTING_POINT_A = 1
    STARTING_POINT_B = 2
    SUB_1 = 3
    SUB_2 = 4
    SUB_3 = 5
    SUB_4 = 6


class MowerFamily(IntEnum):
    """Robomow mower types."""

    Unknown = -1
    RS = 1
    RC = 2
    RX = 3
    RK = 4
    RT = 5


class MowerModel(IntEnum):
    """Robomow mower models."""

    Unknown = -1
    RT300 = 5
    RT500 = 6
    RT700 = 7


@dataclass
class MowerSchedule:
    """Data class representing a Robomow mowing schedule."""

    @dataclass
    class Day:
        """Data class representing a day in the mowing schedule."""

        enabled: bool = True
        cycles: int = 1
        zone: Zone = Zone.MAIN
        duration: int = 30

    start_time: datetime.time = datetime.time(hour=9, minute=0)
    end_time: datetime.time = datetime.time(hour=21, minute=0)
    day: tuple[Day, ...] = field(
        factory=lambda: tuple(MowerSchedule.Day() for _ in range(7))
    )


class MowerOperatingState(StrEnum):
    """Human-readable Robomow operating states."""

    WARMING_UP = "Warming up"
    MOWING = "Mowing"
    EDGE_MOWING = "Edge Mowing"
    RETURNING_HOME_FOLLOWING_EDGE = "Following edge home"
    RETURNING_HOME_WARMING_UP = "Warming up to return home"
    RETURNING_HOME_SEARCHING_EDGE = "Searching edge"

    GOING_TO_START = "Going to starting point"
    LEARNING_ENTRY_POINT = "Learning entry point"
    IDLE = "Idle"
    CHARGING = "Charging"
    AUTOMATIC = "Automatic"
    REMOTE_CONTROL = "Remote control"
    BIT = "Bit"


class EntityKey(StrEnum):
    """Entity keys for all Robomow entities."""

    LAWN_MOWER = "lawn_mower"
    BATTERY_LEVEL = "battery_level"
    FAMILY = "family"
    MODEL = "model"
    SOFTWARE_VERSION = "software_version"
    SOFTWARE_RELEASE = "software_release"
    MAINBOARD_VERSION = "mainboard_version"
    STATE = "state"
    MESSAGE = "message"
    SIGNAL_STRENGTH = "signal_strength"
    START_MOWING = "async_start_mowing"
    STOP_MOWING = "async_stop_mowing"
    RETURN_HOME = "return_home"
    EDGE_MOWING = "edge_mowing"
    SCHEDULE_ENABLED = "schedule_enabled"
    SCHEDULE = "schedule"
    SERVICE_INFO = "service_info"
    NEXT_DEPARTURE = "next_departure"
    PREVIOUS_DEPARTURE = "previous_departure"
    EXPECTED_DURATION = "expected_duration"
    NO_DEPART_REASON = "no_depart_reason"
    ANTI_THEFT_ENABLED = "anti_theft_enabled"
    CHILD_LOCK_ENABLED = "child_lock_enabled"
    ANTI_THEFT_ACTIVE = "anti_theft_active"
    MOWER_HOME = "mower_home"
    CHARGING_ACTIVE = "charging_active"
    DISABLING_DEVICE_REMOVED = "disabling_device_removed"
    WIRE_SIGNAL_TYPE = "wire_signal_type"
    STARTING_POINT_A = "starting_point_a"
    STARTING_POINT_B = "starting_point_b"
    LAST_OPERATIONS = "last_operations"


@dataclass
class MowerOperation:
    """A single parsed mower operation history entry."""

    id: int
    start_time: datetime.datetime
    duration: int
    zone: Zone
    error: Message


@dataclass(frozen=True)
class Message:
    """Base class for user-facing messages with optional title and text."""

    title: str
    text: str | None = None
    number: int | None = None

    def __str__(self) -> str:
        """Return a user-friendly string representation of the message."""
        return f"{self.title} - {self.text}" if self.text else self.title
