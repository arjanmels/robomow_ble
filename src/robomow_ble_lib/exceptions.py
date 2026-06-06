"""Package-specific exception types for Robomow BLE protocol handling."""


class RobomowProtocolError(Exception):
    """Base protocol error."""


class RobomowAuthenticationError(RobomowProtocolError):
    """Raised when BLE authentication fails."""
