"""BLE device data structures for the Robomow integration."""

from __future__ import annotations

import asyncio
import struct
from collections import deque
from contextlib import suppress
from datetime import datetime, timedelta
from typing import TYPE_CHECKING, Any, ClassVar, NamedTuple

from bleak.exc import (
    BleakCharacteristicNotFoundError,
    BleakError,
)
from bleak_retry_connector import (
    BleakClientWithServiceCache,
    establish_connection,
)

from .const import (
    AUTH_RESPONSE_LENGTH,
    LOGGER,
    MESSAGE_RECEIVE_BYTE,
    MESSAGE_SEND_BYTE,
    MESSAGE_START_BYTE,
    MINIMUM_MESSAGE_LENGTH,
    UNKNOWN_FIELD_VALUE,
    UUID_CHAR_AUTHENTICATE,
    UUID_CHAR_DATA_IN,
    UUID_CHAR_DATA_OUT,
    UUID_SERVICE,
    EntityKey,
    Message,
    MessageType,
    MowerFamily,
    MowerModel,
    MowerOperatingState,
    MowerOperation,
    MowerSchedule,
    WireSignalType,
    Zone,
)
from .exceptions import RobomowAuthenticationError
from .family_handler_rt import RobomowRtFamilyHandler
from .helpers import check_payload_length

if TYPE_CHECKING:
    from collections.abc import Callable, Coroutine

    from bleak.backends.characteristic import BleakGATTCharacteristic
    from bleak.backends.device import BLEDevice
    from bleak.backends.service import BleakGATTService

    from .family_handler_base import RobomowFamilyHandler


class RobomowUpdate(NamedTuple):
    """Structured update payload for entity state changes."""

    key: EntityKey
    value: Any


if TYPE_CHECKING:
    type RobomowUpdateCallback = Callable[[RobomowUpdate], None]


RESPONSE_COMMAND_COUNTER_SIZE = 2
GET_CONFIG_PAYLOAD_MIN_SIZE = 5
MESSAGE_TYPE_STOP_ID_MASK = 0x2


class PendingCommand(NamedTuple):
    """Command metadata kept in the pending-response FIFO queue."""

    counter: int
    msg_type: MessageType
    payload: bytes | bytearray | memoryview


class RobomowDevice:
    """Base representation of a Robomow BLE device."""

    _AUTOMATIC_OPERATION_LABELS: ClassVar[dict[int, MowerOperatingState]] = {
        0: MowerOperatingState.WARMING_UP,
        1: MowerOperatingState.GOING_TO_START,
        2: MowerOperatingState.MOWING,
        3: MowerOperatingState.EDGE_MOWING,
        4: MowerOperatingState.RETURNING_HOME_WARMING_UP,
        5: MowerOperatingState.RETURNING_HOME_FOLLOWING_EDGE,
        6: MowerOperatingState.RETURNING_HOME_SEARCHING_EDGE,
        7: MowerOperatingState.LEARNING_ENTRY_POINT,
    }
    _OPERATING_STATE_AUTOMATIC: ClassVar[int] = 3
    _OPERATING_STATE_LABELS: ClassVar[dict[int, MowerOperatingState]] = {
        1: MowerOperatingState.IDLE,
        2: MowerOperatingState.CHARGING,
        _OPERATING_STATE_AUTOMATIC: MowerOperatingState.AUTOMATIC,
        4: MowerOperatingState.REMOTE_CONTROL,
        5: MowerOperatingState.BIT,
    }
    STATE_LABELS: ClassVar[list[str]] = [
        *(state.value for state in _OPERATING_STATE_LABELS.values()),
        *(state.value for state in _AUTOMATIC_OPERATION_LABELS.values()),
    ]

    def __init__(
        self,
        address: str,
        mainboard_serial: str,
        update_callback: RobomowUpdateCallback | None,
    ) -> None:
        """Initialize the device."""
        self._address: str = address
        self._mainboard_serial: bytes = (
            mainboard_serial.strip().encode("utf-8") + b"\x00"
        )
        self._update_callback: RobomowUpdateCallback | None = update_callback

        self._client: BleakClientWithServiceCache | None = None
        self._service: BleakGATTService | None = None
        self._char_auth: BleakGATTCharacteristic | None = None
        self._char_data_in: BleakGATTCharacteristic | None = None
        self._char_data_out: BleakGATTCharacteristic | None = None
        self._command_counter: int = 0
        self._pending_commands: deque[PendingCommand] = deque()
        self._receive_buffer: bytearray = bytearray()
        self._connect_lock = asyncio.Lock()
        self._connect_task_lock = asyncio.Lock()
        self._connect_task: asyncio.Task[None] | None = None
        self._date_time_poll_cancel: Callable[[], None] | None = None
        self._status_poll_cancel: Callable[[], None] | None = None
        self._family_handler: RobomowFamilyHandler | None = None

        self._family: MowerFamily | None = None
        self._model: MowerModel | None = None
        self._software_version: int | None = None
        self._software_release: int | None = None
        self._mainboard_version: int | None = None
        self._schedule_enabled: bool | None = None
        self._message: Message | None = None
        self._operating_state: MowerOperatingState | str | None = None
        self._battery_level: int | None = None
        self._rssi: int | None = None
        self._next_departure: int | None = None
        self._previous_departure: int | None = None
        self._expected_duration: int | None = None
        self._no_depart_reason: str | None = None
        self._anti_theft_enabled: bool | None = None
        self._child_lock_enabled: bool | None = None
        self._anti_theft_active: bool | None = None
        self._mower_home: bool | None = None
        self._charging_active: bool | None = None
        self._disabling_device_removed: bool | None = None
        self._wire_signal_type: WireSignalType | None = None
        self._starting_point_a: int | None = None
        self._starting_point_b: int | None = None
        self._schedule: MowerSchedule | None = None
        self._last_operations: list[MowerOperation] = []

    # --- State listeners ---

    def _data_changed(self, entity_key: EntityKey, value: Any) -> None:
        """Notify listeners that the mower data has changed."""
        if self._update_callback is not None:
            self._update_callback(RobomowUpdate(entity_key, value))

    def _set_schedule_enabled(self, enabled: bool | None) -> None:  # noqa: FBT001
        """Update schedule_enabled and emit change callbacks when needed."""
        if self._schedule_enabled == enabled:
            return
        self._schedule_enabled = enabled
        self._data_changed(EntityKey.SCHEDULE_ENABLED, enabled)

    def _set_schedule(self, schedule: MowerSchedule | None) -> None:
        """Update the mower schedule and emit change callbacks when needed."""
        if self._schedule == schedule:
            return

        self._schedule = schedule
        self._data_changed(EntityKey.SCHEDULE, schedule)

    def _set_last_operations(self, operations: list[MowerOperation]) -> None:
        """Update last-operations history and emit change callbacks when needed."""
        self._last_operations = operations
        self._data_changed(EntityKey.LAST_OPERATIONS, operations)

    def _set_anti_theft_enabled(self, enabled: bool | None) -> None:  # noqa: FBT001
        """Update anti_theft_enabled and emit change callbacks when needed."""
        if self._anti_theft_enabled == enabled:
            return
        self._anti_theft_enabled = enabled
        self._data_changed(EntityKey.ANTI_THEFT_ENABLED, enabled)

    def _set_child_lock_enabled(self, enabled: bool | None) -> None:  # noqa: FBT001
        """Update child_lock_enabled and emit change callbacks when needed."""
        if self._child_lock_enabled == enabled:
            return
        self._child_lock_enabled = enabled
        self._data_changed(EntityKey.CHILD_LOCK_ENABLED, enabled)

    def _set_anti_theft_active(self, active: bool | None) -> None:  # noqa: FBT001
        """Update anti_theft_active and emit change callbacks when needed."""
        if self._anti_theft_active == active:
            return
        self._anti_theft_active = active
        self._data_changed(EntityKey.ANTI_THEFT_ACTIVE, active)

    def _set_mower_home(self, is_home: bool | None) -> None:  # noqa: FBT001
        """Update mower_home and emit change callbacks when needed."""
        if self._mower_home == is_home:
            return
        self._mower_home = is_home
        self._data_changed(EntityKey.MOWER_HOME, is_home)

    def _set_charging_active(self, active: bool | None) -> None:  # noqa: FBT001
        """Update charging_active and emit change callbacks when needed."""
        if self._charging_active == active:
            return
        self._charging_active = active
        self._data_changed(EntityKey.CHARGING_ACTIVE, active)

    def _set_disabling_device_removed(self, removed: bool | None) -> None:  # noqa: FBT001
        """Update disabling_device_removed and emit change callbacks when needed."""
        if self._disabling_device_removed == removed:
            return
        self._disabling_device_removed = removed
        self._data_changed(EntityKey.DISABLING_DEVICE_REMOVED, removed)

    def _set_wire_signal_type(self, wire_signal_type: WireSignalType | None) -> None:
        """Update wire signal type and emit change callbacks when needed."""
        if self._wire_signal_type == wire_signal_type:
            return
        self._wire_signal_type = wire_signal_type
        self._data_changed(EntityKey.WIRE_SIGNAL_TYPE, wire_signal_type)

    def _set_starting_point_a(self, value: int | None) -> None:
        """Update starting point A and emit change callbacks when needed."""
        if self._starting_point_a == value:
            return
        self._starting_point_a = value
        self._data_changed(EntityKey.STARTING_POINT_A, value)

    def _set_starting_point_b(self, value: int | None) -> None:
        """Update starting point B and emit change callbacks when needed."""
        if self._starting_point_b == value:
            return
        self._starting_point_b = value
        self._data_changed(EntityKey.STARTING_POINT_B, value)

    # NOTE: user message clearing behavior is not implemented yet.
    def _set_message(self, message: Message | None) -> None:
        """Update message text and emit change callbacks when needed."""
        if self._message == message:
            return
        self._message = message
        self._data_changed(EntityKey.MESSAGE, message)

    def _set_state(self, operating_state: MowerOperatingState | str | None) -> None:
        """Update operating state text and emit change callbacks when needed."""
        if self._operating_state == operating_state:
            return
        self._operating_state = operating_state
        self._data_changed(EntityKey.STATE, operating_state)

    def _set_rssi(self, rssi: int | None) -> None:
        """Update RSSI value and emit change callbacks when needed."""
        if self._rssi == rssi:
            return
        self._rssi = rssi
        self._data_changed(EntityKey.SIGNAL_STRENGTH, rssi)

    def _set_battery_level(self, battery_level: int | None) -> None:
        """Update battery level when it changes."""
        if self._battery_level == battery_level:
            return
        self._battery_level = battery_level
        self._data_changed(EntityKey.BATTERY_LEVEL, battery_level)

    def _set_next_departure(self, value: int | None) -> None:
        """Update next departure and emit change callbacks when needed."""
        if self._next_departure == value:
            return
        if value == UNKNOWN_FIELD_VALUE:
            self._next_departure = None
        else:
            self._next_departure = value
        self._data_changed(EntityKey.NEXT_DEPARTURE, self._next_departure)

    def _set_previous_departure(self, value: int | None) -> None:
        """Update previous departure and emit change callbacks when needed."""
        if self._previous_departure == value:
            return
        if value == UNKNOWN_FIELD_VALUE:
            self._previous_departure = None
        else:
            self._previous_departure = value
        self._data_changed(EntityKey.PREVIOUS_DEPARTURE, self._previous_departure)

    def _set_expected_duration(self, value: int | None) -> None:
        """Update expected duration and emit change callbacks when needed."""
        if self._expected_duration == value:
            return
        self._expected_duration = value
        self._data_changed(EntityKey.EXPECTED_DURATION, self._expected_duration)

    def _set_no_depart_reason(self, value: str | None) -> None:
        """Update no-depart reason and emit change callbacks when needed."""
        if self._no_depart_reason == value:
            return
        self._no_depart_reason = value
        self._data_changed(EntityKey.NO_DEPART_REASON, value)

    async def _async_set_family(self, value: MowerFamily | int | None) -> None:
        """Update mower family and select a family-specific protocol handler."""
        family = None if value is None else MowerFamily(value)
        if self._family == family:
            return

        self._family = family
        self._data_changed(EntityKey.FAMILY, self._family)

        if family is None:
            self._family_handler = None
            LOGGER.warning("Mower family is unknown; using base protocol handler")
            return

        if family is MowerFamily.RT:
            target_handler_cls = RobomowRtFamilyHandler
        else:
            self._family_handler = None
            LOGGER.warning(
                "No protocol handler registered for mower family %s; "
                "using base handler",
                family.name,
            )
            return

        current_handler = self._family_handler
        if isinstance(current_handler, target_handler_cls):
            return

        LOGGER.debug(
            "Switching mower protocol handler from %s to %s for family %s",
            (
                current_handler.__class__.__name__
                if current_handler is not None
                else "None"
            ),
            target_handler_cls.__name__,
            family.name,
        )
        self._family_handler = target_handler_cls(self)
        await self._async_initialize_family_state()

    def _set_model(self, value: MowerModel | int | None) -> None:
        """Update mower model and emit change callbacks when needed."""
        model = None if value is None else MowerModel(value)
        if self._model == model:
            return
        self._model = model
        # Model changes may imply a family change, so update both.
        self._data_changed(EntityKey.MODEL, self._model)

    def _set_software_version(self, value: int | None) -> None:
        """Update software version and emit change callbacks when needed."""
        if self._software_version == value:
            return
        self._software_version = value
        self._data_changed(EntityKey.SOFTWARE_VERSION, self._software_version)

    def _set_software_release(self, value: int | None) -> None:
        """Update software release and emit change callbacks when needed."""
        if self._software_release == value:
            return
        self._software_release = value
        self._data_changed(EntityKey.SOFTWARE_RELEASE, self._software_release)

    def _set_mainboard_version(self, value: int | None) -> None:
        """Update mainboard version and emit change callbacks when needed."""
        if self._mainboard_version == value:
            return
        self._mainboard_version = value
        self._data_changed(EntityKey.MAINBOARD_VERSION, self._mainboard_version)

    def _describe_operating_state(
        self, state: int, operation: int
    ) -> MowerOperatingState | str:
        """Return human-readable text for the mower operating state."""
        if state == self._OPERATING_STATE_AUTOMATIC:
            return self._AUTOMATIC_OPERATION_LABELS.get(
                operation, f"Unknown Automatic ({operation})"
            )
        return self._OPERATING_STATE_LABELS.get(state, f"Unknown ({state})")

    # --- Internal state helpers ---

    def _cancel_periodic_polling(self) -> None:
        """Cancel all active periodic polling callbacks."""
        if self._date_time_poll_cancel is not None:
            self._date_time_poll_cancel()
            self._date_time_poll_cancel = None

        if self._status_poll_cancel is not None:
            self._status_poll_cancel()
            self._status_poll_cancel = None

    def _initialize_runtime_state(self) -> None:
        """Initialize runtime state after a successful BLE connection."""
        self._command_counter = 0
        self._pending_commands.clear()
        self._receive_buffer.clear()
        self._set_message(None)
        self._set_state(None)
        self._set_battery_level(None)
        self._set_schedule_enabled(None)
        self._set_rssi(None)
        self._set_next_departure(None)
        self._set_previous_departure(None)
        self._set_expected_duration(None)
        self._set_no_depart_reason(None)
        self._set_anti_theft_enabled(None)
        self._set_child_lock_enabled(None)
        self._set_anti_theft_active(None)
        self._set_mower_home(None)
        self._set_charging_active(None)
        self._set_disabling_device_removed(None)
        self._set_wire_signal_type(None)
        self._set_starting_point_a(None)
        self._set_starting_point_b(None)

    def _teardown_connection(self) -> None:
        """Clear connection state, cancel polling, and notify listeners."""
        self._client = None
        self._service = None
        self._char_auth = None
        self._char_data_in = None
        self._char_data_out = None
        self._initialize_runtime_state()

    async def _async_establish_client_connection(self, ble_device: BLEDevice) -> None:
        """Resolve BLE device and establish a paired client connection."""
        self._client = await establish_connection(
            BleakClientWithServiceCache,
            ble_device,
            ble_device.address,
            disconnected_callback=self._handle_disconnect,
            pair=True,
        )

    def _resolve_characteristics(self) -> None:
        """Resolve GATT service and required characteristics for this device."""
        if self._client is None:
            return

        self._service = self._client.services.get_service(UUID_SERVICE)
        if self._service is None:
            raise BleakCharacteristicNotFoundError(UUID_SERVICE)

        self._char_auth = self._service.get_characteristic(UUID_CHAR_AUTHENTICATE)
        if self._char_auth is None:
            raise BleakCharacteristicNotFoundError(UUID_CHAR_AUTHENTICATE)

        self._char_data_in = self._service.get_characteristic(UUID_CHAR_DATA_IN)
        if self._char_data_in is None:
            raise BleakCharacteristicNotFoundError(UUID_CHAR_DATA_IN)

        self._char_data_out = self._service.get_characteristic(UUID_CHAR_DATA_OUT)
        if self._char_data_out is None:
            raise BleakCharacteristicNotFoundError(UUID_CHAR_DATA_OUT)

    async def _async_authenticate_connection(self) -> None:
        """Authenticate by writing the mainboard serial and validating response."""
        if self._client is None:
            return
        if self._char_auth is None:
            raise BleakCharacteristicNotFoundError(UUID_CHAR_AUTHENTICATE)

        await self._client.write_gatt_char(
            self._char_auth, self._mainboard_serial, response=True
        )

        auth_response = await self._client.read_gatt_char(self._char_auth)
        if auth_response != bytes([0x01] * AUTH_RESPONSE_LENGTH):
            LOGGER.debug(
                "Authentication failed: invalid response payload: %s",
                auth_response.hex(),
            )
            raise RobomowAuthenticationError

    async def _async_start_notifications(self) -> None:
        """Start notifications for incoming mower packets."""
        if self._client is None:
            return
        if self._char_data_in is None:
            raise BleakCharacteristicNotFoundError(UUID_CHAR_DATA_IN)

        await self._client.start_notify(
            self._char_data_in,
            self._async_handle_data_received,
        )

    @property
    def address(self) -> str:
        """Return the device address."""
        return self._address

    @property
    def mainboard_serial(self) -> str:
        """Return the mainboard serial number."""
        return self._mainboard_serial.decode("utf-8").rstrip("\x00")

    @property
    def family(self) -> MowerFamily:
        """Return the mower family, if known."""
        return self._family or MowerFamily.Unknown

    @property
    def model(self) -> MowerModel:
        """Return the mower model, if known."""
        return self._model or MowerModel.Unknown

    @property
    def mainboard_version(self) -> int | None:
        """Return the mainboard version, if known."""
        return self._mainboard_version

    @property
    def software_version(self) -> int | None:
        """Return the software version, if known."""
        return self._software_version

    @property
    def software_release(self) -> int | None:
        """Return the software release, if known."""
        return self._software_release

    @property
    def schedule_enabled(self) -> bool | None:
        """Return whether the mower schedule is enabled, if known."""
        return self._schedule_enabled

    @property
    def schedule(self) -> MowerSchedule | None:
        """Return the mower schedule, if known."""
        return self._schedule

    @property
    def last_operations(self) -> list[MowerOperation]:
        """Return the mower's last operations history, newest-first."""
        return self._last_operations

    @property
    def anti_theft_enabled(self) -> bool | None:
        """Return whether anti-theft is enabled, if known."""
        return self._anti_theft_enabled

    @property
    def child_lock_enabled(self) -> bool | None:
        """Return whether child lock is enabled, if known."""
        return self._child_lock_enabled

    @property
    def anti_theft_active(self) -> bool | None:
        """Return whether anti-theft is currently active, if known."""
        return self._anti_theft_active

    @property
    def mower_home(self) -> bool | None:
        """Return whether mower is currently at home, if known."""
        return self._mower_home

    @property
    def charging_active(self) -> bool | None:
        """Return whether charging is currently active, if known."""
        return self._charging_active

    @property
    def message(self) -> Message | None:
        """Return the latest mower status text, if known."""
        return self._message

    @property
    def operating_state(self) -> MowerOperatingState | str | None:
        """Return the latest mower operating state text, if known."""
        return self._operating_state

    @property
    def battery_level(self) -> int | None:
        """Return the latest battery level percentage, if known."""
        return self._battery_level

    @property
    def next_departure(self) -> int | None:
        """Return the next scheduled departure time, if known."""
        return self._next_departure

    @property
    def previous_departure(self) -> int | None:
        """Return the previous departure time, if known."""
        return self._previous_departure

    @property
    def expected_duration(self) -> int | None:
        """Return the expected mowing duration, if known."""
        return self._expected_duration

    @property
    def no_depart_reason(self) -> str | None:
        """Return the reason the mower has not departed, if known."""
        return self._no_depart_reason

    @property
    def rssi(self) -> int | None:
        """Return the latest RSSI value, if known."""
        return self._rssi

    def is_connected(self) -> bool:
        """Return True if the client is connected."""
        return self._client is not None and self._client.is_connected

    # --- Connection lifecycle ---

    async def _async_connect_worker(self, device: BLEDevice) -> None:
        """Perform a single serialized connect attempt."""
        async with self._connect_lock:
            if self._client is not None and self._client.is_connected:
                LOGGER.debug("BLE client already connected")
                return

            LOGGER.debug("Connecting to Robomow BLE device")

            try:
                await self._async_establish_client_connection(device)
                self._resolve_characteristics()
                await self._async_authenticate_connection()
                await self._async_start_notifications()
            except BleakError:
                await self._async_disconnect_unlocked()
                raise

            self._initialize_runtime_state()

            await self._async_initialize_family_state()

            self._start_status_polling()
            self._start_date_time_polling()



    async def async_connect(self, device: BLEDevice) -> None:
        """Create and connect a Robomow BLE client."""
        async with self._connect_task_lock:
            if self._connect_task is None or self._connect_task.done():
                self._connect_task = asyncio.create_task(
                    self._async_connect_worker(device)
                )
            connect_task = self._connect_task

        with suppress(asyncio.CancelledError):
            await connect_task

    async def _async_disconnect_unlocked(self) -> None:
        """Disconnect without acquiring the connect lock."""
        LOGGER.debug("BLE client disconnect called")
        self._cancel_periodic_polling()
        if self._client is not None and self._client.is_connected:
            if self._char_data_in is not None:
                await self._client.stop_notify(self._char_data_in)
            await self._client.disconnect()

    async def async_disconnect(self) -> None:
        """Disconnect the BLE client."""
        async with self._connect_task_lock:
            connect_task = self._connect_task
            self._connect_task = None

        if connect_task is not None and not connect_task.done():
            connect_task.cancel()
            with suppress(asyncio.CancelledError):
                await connect_task

        async with self._connect_lock:
            await self._async_disconnect_unlocked()

    # --- Packet I/O ---

    async def _async_write_value(self, data: bytes) -> bool:
        """Write a packet payload to the mower data output characteristic."""
        if not self.is_connected() or not self._client or not self._char_data_out:
            return False

        try:
            for start in range(0, len(data), 20):
                await self._client.write_gatt_char(
                    self._char_data_out, data[start : start + 20], response=True
                )
        except BleakError as err:
            LOGGER.error("Error writing data: %s", err)
            return False
        return True

    @staticmethod
    def _calculate_checksum(data: bytes | bytearray | memoryview) -> int:
        """Calculate packet checksum by XORing 0xFF with the byte sum."""
        return (~sum(data)) & 0xFF

    async def _async_send_msg(
        self,
        msg_type: MessageType,
        payload: bytes | bytearray | memoryview | None = None,
    ) -> bool:
        """Update packet checksum and write it to the BLE characteristic."""
        payload = payload or b""

        LOGGER.debug("Sending  %-15s: %s", msg_type.name, payload.hex())

        packet = struct.pack(
            ">BBBB", MESSAGE_START_BYTE, 5 + len(payload), MESSAGE_SEND_BYTE, msg_type
        )
        packet += payload
        packet += struct.pack(">B", self._calculate_checksum(packet))

        return await self._async_write_value(packet)

    async def _async_send_msg_with_sequence(
        self, msg_type: MessageType, payload: bytes | bytearray | memoryview
    ) -> bool:
        """Send a message with a 2-byte command counter and the given payload."""
        command_counter = self._command_counter = self._command_counter + 1
        buf = struct.pack(">H", command_counter) + payload
        pending_command = PendingCommand(command_counter, msg_type, payload)
        self._pending_commands.append(pending_command)
        sent = await self._async_send_msg(msg_type, buf)
        if not sent:
            with suppress(ValueError):
                self._pending_commands.remove(pending_command)

        return sent

    async def _async_send_misc_msg(
        self, misc_type: int, payload: bytes | bytearray | memoryview | None = None
    ) -> bool:
        """Send a miscellaneous message with the given type and command counter."""
        return await self._async_send_msg_with_sequence(
            MessageType.MISCELLANEOUS, struct.pack(">H", misc_type) + (payload or b"")
        )

    # --- Polling ---

    def _start_periodic_poll(
        self,
        action: Callable[[], Coroutine[Any, Any, Any]],
        interval: timedelta,
    ) -> Callable[[], None]:
        """Run an async action repeatedly without overlapping executions."""
        interval_seconds = interval.total_seconds()
        cancelled = False
        runner_task: asyncio.Task[Any] | None = None

        async def _runner() -> None:
            while not cancelled:
                try:
                    await action()
                except asyncio.CancelledError:
                    raise
                except Exception:  # noqa: BLE001
                    LOGGER.exception("Periodic poll action failed")

                if cancelled:
                    break
                await asyncio.sleep(interval_seconds)

        runner_task = asyncio.create_task(_runner())

        def _cancel() -> None:
            nonlocal cancelled, runner_task
            cancelled = True
            if runner_task is not None:
                runner_task.cancel()

        return _cancel

    def _start_date_time_polling(self) -> None:
        """Start sending date/time updates every minute while connected."""
        if not self.is_connected():
            return

        self._date_time_poll_cancel = self._start_periodic_poll(
            self.async_update_date_time,
            timedelta(seconds=60),
        )

    async def async_update_date_time(self, timestamp: datetime | None = None) -> bool:
        """Update mower date and time."""
        timestamp = timestamp or datetime.now().astimezone()
        return await self._async_send_msg_with_sequence(
            MessageType.UPDATE_DATE_TIME,
            struct.pack(
                ">HBBHBBB",
                1,
                timestamp.day,
                timestamp.month,
                timestamp.year,
                timestamp.hour,
                timestamp.minute,
                0,
            ),
        )

    def _start_status_polling(self) -> None:
        """Start sending GET_STATUS every 2 seconds while connected."""
        if not self.is_connected():
            return

        self._status_poll_cancel = self._start_periodic_poll(
            self._async_poll_family_status,
            timedelta(seconds=2),
        )

    async def _async_initialize_family_state(self) -> None:
        """Initialize family-specific state after connection."""
        if self._family_handler is not None:
            await self._family_handler.async_initialize_state()
            return
        await self._async_send_msg(MessageType.GET_CONFIG)

    async def _async_poll_family_status(self) -> None:
        """Poll family-specific status while connected."""
        if self._family_handler is not None:
            await self._family_handler.async_poll_status()

    async def _async_read_eeprom_param(self, *params: int) -> bool:
        """Send a message to read one or more EEPROM parameters by ID."""
        if not params:
            return False

        payload = struct.pack(
            f">{len(params)}H",
            *(int(param) for param in params),
        )
        return await self._async_send_msg_with_sequence(
            MessageType.READ_EEPROM,
            payload,
        )

    async def _async_write_eeprom_param(self, param: int, value: int) -> bool:
        """Send a message to write an EEPROM parameter with the given ID and value."""
        return await self._async_send_msg_with_sequence(
            MessageType.WRITE_EEPROM, struct.pack(">HL", param, value)
        )

    async def async_enable_schedule(self) -> None:
        """Enable mower schedule for the active mower family."""
        if self._family_handler is not None:
            await self._family_handler.async_enable_schedule()
            return
        msg = f"enable_schedule not implemented for family {self.family.name}"
        raise NotImplementedError(msg)

    async def async_disable_schedule(self) -> None:
        """Disable mower schedule for the active mower family."""
        if self._family_handler is not None:
            await self._family_handler.async_disable_schedule()
            return
        msg = f"disable_schedule not implemented for family {self.family.name}"
        raise NotImplementedError(msg)

    async def async_enable_anti_theft(self) -> None:
        """Enable anti-theft for the active mower family."""
        if self._family_handler is not None:
            await self._family_handler.async_enable_anti_theft()
            return
        msg = f"enable_anti_theft not implemented for family {self.family.name}"
        raise NotImplementedError(msg)

    async def async_disable_anti_theft(self) -> None:
        """Disable anti-theft for the active mower family."""
        if self._family_handler is not None:
            await self._family_handler.async_disable_anti_theft()
            return
        msg = f"disable_anti_theft not implemented for family {self.family.name}"
        raise NotImplementedError(msg)

    async def async_enable_child_lock(self) -> None:
        """Enable child lock for the active mower family."""
        if self._family_handler is not None:
            await self._family_handler.async_enable_child_lock()
            return
        msg = f"enable_child_lock not implemented for family {self.family.name}"
        raise NotImplementedError(msg)

    async def async_disable_child_lock(self) -> None:
        """Disable child lock for the active mower family."""
        if self._family_handler is not None:
            await self._family_handler.async_disable_child_lock()
            return
        msg = f"disable_child_lock not implemented for family {self.family.name}"
        raise NotImplementedError(msg)

    async def async_set_wire_signal_type(
        self, wire_signal_type: WireSignalType
    ) -> None:
        """Set wire signal type for the active mower family."""
        if self._family_handler is not None:
            await self._family_handler.async_set_wire_signal_type(wire_signal_type)
            return
        msg = f"set_wire_signal_type not implemented for family {self.family.name}"
        raise NotImplementedError(msg)

    async def async_set_starting_point_a(self, value: int) -> None:
        """Set starting point A for the active mower family."""
        if self._family_handler is not None:
            await self._family_handler.async_set_starting_point_a(value)
            return
        msg = f"set_starting_point_a not implemented for family {self.family.name}"
        raise NotImplementedError(msg)

    async def async_set_starting_point_b(self, value: int) -> None:
        """Set starting point B for the active mower family."""
        if self._family_handler is not None:
            await self._family_handler.async_set_starting_point_b(value)
            return
        msg = f"set_starting_point_b not implemented for family {self.family.name}"
        raise NotImplementedError(msg)

    async def async_set_schedule(self, schedule: MowerSchedule) -> None:
        """Set mowing schedule for the active mower family."""
        if self._family_handler is not None:
            await self._family_handler.async_set_schedule(schedule)
            return
        msg = f"set_schedule not implemented for family {self.family.name}"
        raise NotImplementedError(msg)

    async def async_start_mowing(
        self,
        duration_minutes: int | None = None,
        starting_zone: Zone | None = None,
    ) -> None:
        """Start mowing for the active mower family."""
        if self._family_handler is not None:
            await self._family_handler.async_start_mowing(
                duration_minutes,
                starting_zone,
            )
            return
        msg = f"start_mowing not implemented for family {self.family.name}"
        raise NotImplementedError(msg)

    async def async_start_mowing_edge(self) -> None:
        """Start edge mowing for the active mower family."""
        if self._family_handler is not None:
            await self._family_handler.async_start_mowing_edge()
            return
        msg = f"start_mowing_edge not implemented for family {self.family.name}"
        raise NotImplementedError(msg)

    async def async_stop_mowing(self) -> None:
        """Stop mowing for the active mower family."""
        if self._family_handler is not None:
            await self._family_handler.async_stop_mowing()
            return
        msg = f"stop_mowing not implemented for family {self.family.name}"
        raise NotImplementedError(msg)

    async def async_return_to_home(self) -> None:
        """Return mower home for the active mower family."""
        if self._family_handler is not None:
            await self._family_handler.async_return_to_home()
            return
        msg = f"return_to_home not implemented for family {self.family.name}"
        raise NotImplementedError(msg)

    def _pop_pending_command(
        self, command_counter: int, msg_type: MessageType
    ) -> PendingCommand | None:
        """Pop the matching pending command for a response command counter."""
        for index, pending in enumerate(self._pending_commands):
            if pending.counter != command_counter:
                continue

            skipped = [self._pending_commands.popleft() for _ in range(index)]
            if skipped:
                LOGGER.warning(
                    "Detected %d missing response(s) before command counter 0x%04X: %s",
                    len(skipped),
                    command_counter,
                    ", ".join(f"0x{command.counter:04X}" for command in skipped),
                )

            cmd = self._pending_commands.popleft()
            if msg_type not in (MessageType.ACKNOWLEDGE, cmd.msg_type):
                LOGGER.warning(
                    "Expected response of type %s for command counter 0x%04X but got "
                    "type %s",
                    cmd.msg_type.name,
                    command_counter,
                    msg_type.name,
                )
                return None
            return cmd

        return None

    # --- BLE event handlers ---

    def _handle_disconnect(self, _client: BleakClientWithServiceCache) -> None:
        """Handle BLE disconnect callback."""
        LOGGER.debug("BLE client disconnected")
        self._cancel_periodic_polling()
        self._teardown_connection()

    async def _async_handle_data_received(
        self,
        _sender: object,
        data: bytearray,
    ) -> None:
        """Handle BLE notifications."""
        self._receive_buffer.extend(data)

        while len(self._receive_buffer) >= MINIMUM_MESSAGE_LENGTH:
            if (
                self._receive_buffer[0] != MESSAGE_START_BYTE
                or self._receive_buffer[2] != MESSAGE_RECEIVE_BYTE
            ):
                LOGGER.warning(
                    "Received malformed packet: %s",
                    self._receive_buffer.hex(),
                )
                del self._receive_buffer[0]
                continue

            packet_len = self._receive_buffer[1]
            if len(self._receive_buffer) < packet_len:
                return

            packet = self._receive_buffer[:packet_len]
            self._receive_buffer = self._receive_buffer[packet_len:]

            if self._calculate_checksum(packet[:-1]) != packet[-1]:
                LOGGER.warning(
                    "Received packet with invalid checksum: %s",
                    packet.hex(),
                )
                continue

            try:
                msg_type = MessageType(packet[3])
            except ValueError:
                LOGGER.warning(
                    "Received packet with unknown msg_type 0x%02X: %s",
                    packet[3],
                    packet.hex(),
                )
                continue

            await self._async_process_message(msg_type, packet[4:-1])

    async def _async_process_message(
        self, msg_type: MessageType, payload: bytes | bytearray | memoryview
    ) -> None:
        """Dispatch a complete received packet to the appropriate handler."""
        LOGGER.debug("Received %-15s: %s", msg_type.name, payload.hex())

        if msg_type == MessageType.GET_CONFIG:
            await self._async_handle_get_config(payload)
        elif msg_type == MessageType.GET_MESSAGE:
            self._handle_get_message(payload)
        elif msg_type in (
            MessageType.ACKNOWLEDGE,
            MessageType.MISCELLANEOUS,
            MessageType.READ_EEPROM,
        ):
            self._handle_sequenced_response(msg_type, payload)

    async def _async_handle_get_config(
        self, payload: bytes | bytearray | memoryview
    ) -> None:
        """Handle GET_CONFIG for family detection and shared version fields."""
        if not check_payload_length(
            MessageType.GET_CONFIG, payload, GET_CONFIG_PAYLOAD_MIN_SIZE
        ):
            return

        (
            family,
            software_version,
            software_release,
            mainboard_version,
        ) = struct.unpack_from(">BBHB", payload)
        await self._async_set_family(family)
        self._set_software_version(software_version)
        self._set_software_release(software_release)
        self._set_mainboard_version(mainboard_version)

    def _handle_get_message(self, payload: bytes | bytearray | memoryview) -> None:
        """Handle a GET_MESSAGE response packet for the active mower family."""
        if self._family_handler is not None:
            self._family_handler.handle_get_message(payload)
            return
        LOGGER.debug(
            "Ignoring GET_MESSAGE for unsupported family handler: %s",
            payload.hex(),
        )

    def _handle_sequenced_response(
        self, msg_type: MessageType, payload: bytes | bytearray | memoryview
    ) -> None:
        """Handle a sequenced response: extract counter, match command, delegate."""
        if not check_payload_length(msg_type, payload, RESPONSE_COMMAND_COUNTER_SIZE):
            return

        command_counter = struct.unpack_from(">H", payload)[0]
        response = PendingCommand(command_counter, msg_type, payload[2:])

        request = self._pop_pending_command(response.counter, msg_type)
        if not request:
            LOGGER.warning(
                "Received %s response with unknown command counter 0x%04X",
                msg_type.name,
                command_counter,
            )
            return

        if msg_type == MessageType.READ_EEPROM:
            self._handle_read_eeprom_response(request, response)
        elif msg_type == MessageType.MISCELLANEOUS:
            self._handle_miscellaneous_response(request, response)
        elif msg_type == MessageType.ACKNOWLEDGE:
            pass  # No additional handling needed for ACKNOWLEDGE responses
        else:
            LOGGER.warning(
                "Received %s response with unhandled msg_type for command counter "
                "0x%04X: %s => %s",
                request.msg_type.name,
                command_counter,
                request.payload.hex(),
                response.payload.hex(),
            )

    def _handle_read_eeprom_response(
        self, request: PendingCommand, response: PendingCommand
    ) -> None:
        """Handle READ_EEPROM for the active mower family."""
        if self._family_handler is not None:
            self._family_handler.handle_read_eeprom_response(request, response)
            return
        LOGGER.debug(
            "Ignoring READ_EEPROM for unsupported family handler: %s => %s",
            request.payload.hex(),
            response.payload.hex(),
        )

    def _handle_miscellaneous_response(
        self, request: PendingCommand, response: PendingCommand
    ) -> None:
        """Handle MISCELLANEOUS response for the active mower family."""
        if self._family_handler is not None:
            self._family_handler.handle_miscellaneous_response(response)
            return
        LOGGER.debug(
            "Ignoring MISCELLANEOUS for unsupported family handler: %s => %s",
            request.payload.hex(),
            response.payload.hex(),
        )

    def update_from_rssi(self, rssi: int | None) -> None:
        """Update RSSI from BLE service info."""
        LOGGER.debug(
            "Updating RSSI from service info: %s",
            rssi,
        )
        self._set_rssi(rssi)
