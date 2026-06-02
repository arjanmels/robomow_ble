"""Family-specific protocol handler interfaces for Robomow BLE devices."""

from __future__ import annotations

from abc import ABC, abstractmethod
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from robomow_ble.const import MowerSchedule, Zone

    from .const import WireSignalType
    from .mower import PendingCommand, RobomowDevice


class RobomowFamilyHandler(ABC):
    """Base interface for family-specific Robomow protocol behavior."""

    def __init__(self, device: RobomowDevice) -> None:
        """Initialize RT family handler with a backing device."""
        self._device = device

    @abstractmethod
    async def async_initialize_state(self) -> None:
        """Initialize family-specific state after connection."""

    @abstractmethod
    async def async_poll_status(self) -> None:
        """Poll family-specific status while connected."""

    @abstractmethod
    async def async_enable_schedule(self) -> None:
        """Enable mower schedule."""

    @abstractmethod
    async def async_disable_schedule(self) -> None:
        """Disable mower schedule."""

    @abstractmethod
    async def async_set_schedule(self, schedule: MowerSchedule) -> None:
        """Set mowing schedule."""

    @abstractmethod
    async def async_enable_anti_theft(self) -> None:
        """Enable anti-theft mode."""

    @abstractmethod
    async def async_disable_anti_theft(self) -> None:
        """Disable anti-theft mode."""

    @abstractmethod
    async def async_enable_child_lock(self) -> None:
        """Enable child lock mode."""

    @abstractmethod
    async def async_disable_child_lock(self) -> None:
        """Disable child lock mode."""

    @abstractmethod
    async def async_set_wire_signal_type(
        self, wire_signal_type: WireSignalType
    ) -> None:
        """Set wire signal type."""

    @abstractmethod
    async def async_set_starting_point_a(self, value: int) -> None:
        """Set starting point A."""

    @abstractmethod
    async def async_set_starting_point_b(self, value: int) -> None:
        """Set starting point B."""

    @abstractmethod
    async def async_start_mowing(
        self,
        duration_minutes: int | None = None,
        starting_zone: Zone | None = None,
    ) -> None:
        """Start mowing."""

    @abstractmethod
    async def async_start_mowing_edge(self) -> None:
        """Start edge mowing."""

    @abstractmethod
    async def async_stop_mowing(self) -> None:
        """Stop mowing."""

    @abstractmethod
    async def async_return_to_home(self) -> None:
        """Return mower to home."""

    @abstractmethod
    def handle_get_message(self, payload: bytes | bytearray | memoryview) -> None:
        """Handle GET_MESSAGE payload."""

    @abstractmethod
    def handle_read_eeprom_response(
        self, request: PendingCommand, response: PendingCommand
    ) -> None:
        """Handle READ_EEPROM response payload."""

    @abstractmethod
    def handle_miscellaneous_response(self, response: PendingCommand) -> None:
        """Handle MISCELLANEOUS response payload."""
