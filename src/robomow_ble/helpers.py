"""Shared helper functions for the Robomow BLE package."""

from __future__ import annotations

import logging
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from .const import MessageType

LOGGER: logging.Logger = logging.getLogger(__package__)


def check_payload_length(
    msg_type: MessageType,
    payload: bytes | bytearray | memoryview,
    expected_length: int,
    *,
    exact: bool = False,
) -> bool:
    """Validate payload length and log a warning for invalid packets."""
    is_valid = (
        len(payload) == expected_length if exact else len(payload) >= expected_length
    )
    if not is_valid:
        LOGGER.warning(
            "Payload %s (expected %d, got %d) for %s: %s",
            "length mismatch" if exact else "too short",
            expected_length,
            len(payload),
            msg_type.name,
            payload.hex(),
        )
    return is_valid
