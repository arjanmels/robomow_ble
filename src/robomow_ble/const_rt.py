# ruff: noqa: E501
"""RT-family specific constants and enums for Robomow BLE."""

from __future__ import annotations

from enum import IntEnum
from types import MappingProxyType

from .const import Message

MESSAGE_TYPE_STOP_ID_MASK = 0x2

GET_STATUS_PAYLOAD_SIZE = 7
READ_EEPROM_PAYLOAD_SIZE = 4
INFO_PAYLOAD_SIZE = 5
MISC_TYPE_MIN_SIZE = 2
CONFIG_META_DATA_PAYLOAD_SIZE = MISC_TYPE_MIN_SIZE + 14
STATE_PAYLOAD_SIZE = MISC_TYPE_MIN_SIZE + 15
EXTENDED_STATE_PAYLOAD_SIZE = STATE_PAYLOAD_SIZE + 13

LAST_OPERATIONS_RECORD_SIZE = 14


class OperationType(IntEnum):
    """Operation types used in RT command messages."""

    STOP_MOWING = 0x0000
    START_EDGE_MOWING = 0x0001
    START_MOWING = 0x0002
    RETURN_HOME = 0x0003


class MiscMessageType(IntEnum):
    """RT miscellaneous message sub-types."""

    INFO = 0x08
    STATE = 0x0B
    GET_SCHEDULE = 0x0D
    EXTENDED_STATE = 0x27
    SET_SCHEDULE = 0x3D
    LAST_OPERATIONS = 0x4C
    CONFIG_META_DATA = 0x4E

    # Following message types are nto used (yet)
    LAWN_AREA_ID = 0x05
    ANTI_THEFT_CONFIRM = 0x0C
    USER_MESSAGE_CLEARED = 0x0E
    LAST_OPERATION_SUMMARY = 0x4D
    SUPPORTED_FEATURES = 0x4F
    ZONE_INFO = 0x12
    ENERGY = 0x44
    GSM_LOCATION = 0x50
    GSM_SIGNAL = 0x51
    GSM_STATUS = 0x52
    GSM_POSITION = 0x53


class EepromParam(IntEnum):
    """RT-family EEPROM parameter identifiers."""

    STARTING_POINT_A = 0x000D
    STARTING_POINT_B = 0x000E

    SCHEDULE_ENABLED = 0x008C
    ANTI_THEFT_ENABLED = 0x00B9
    CHILD_LOCK_ENABLED = 0x00BC
    WIRE_SIGNAL_TYPE = 0x011F

def get_message(number: int) -> Message:
    """Look up a regular RT message by code."""
    message = MESSAGES.get(number)
    if message is None:
        return Message(f"Unknown message {number}", number=number)
    return Message(message.title, message.text, number)

def get_error_message(number: int) -> Message:
    """Look up an RT error message by code."""
    message = ERROR_MESSAGES.get(number)
    if message is None:
        return Message(f"Unknown error message {number}", number=number)
    return Message(message.title, message.text, number)

def get_no_depart_message(number: int) -> Message:
    """Look up an RT no-depart message by code."""
    message = NO_DEPART_MESSAGES.get(number)
    if message is None:
        return Message(f"Unknown no-depart message {number}", number=number)
    return Message(message.title, message.text, number)


MESSAGES: MappingProxyType[int, Message] = MappingProxyType(
    {
        0: Message("Success"),
        1: Message("STOP button"),
        2: Message(
            "No wire signal",
            "Make sure the base station is connected to power supply. Disconnect the power supply and reconnect after 10 seconds. Check connection of the perimeter wire to the base station. Check for breaks in the perimeter wire.",
        ),
        3: Message(
            "Place mower inside lawn to start",
            "Please restart operation inside the perimeter wire (3)",
        ),
        5: Message("Bumper was pressed", "Bumper pressed"),
        6: Message("Lift was detected", "Mower needs your help, please restart (6)"),
        7: Message("Stuck In place", "Mower needs your help, please restart (7)"),
        8: Message("Stuck In place", "Mower needs your help, please restart (8)"),
        9: Message(
            "Waiting for power supply",
            "Robot got off the base station because charging voltage is not detected",
        ),
        10: Message(
            "Waiting for power supply",
            "Charging will resume after power supply returns",
        ),
        11: Message(
            "Waiting for power supply",
            "Charging will resume after power supply returns",
        ),
        12: Message("One-time Setup process"),
        13: Message("Drive overheat"),
        14: Message(
            "Docking problem detected",
            "Mower needs your help, place mower in base station and check charging (14)",
        ),
        15: Message("Recharge battery", "Mower needs to be recharged (15)"),
        16: Message("Drive overheat"),
        17: Message("Recharge battery", "Mower needs to be recharged (17)"),
        18: Message("Recharge battery", "Mower needs to be recharged (18)"),
        19: Message(
            "Waiting for power supply",
            "Charging process is halted because charger overheat is detected",
        ),
        20: Message("Too short operations"),
        21: Message("Low Temperature"),
        22: Message(
            "Please start the operation elsewhere",
            "more than 10 drive overcurrent events occurred during scan",
        ),
        23: Message(
            "Please start the operation elsewhere",
            "Mower needs your help, please restart (23)",
        ),
        24: Message("Stuck in place"),
        25: Message(
            "Remove disabling key before lifting",
            "Mower needs your help, please restart operation (25)",
        ),
        26: Message("System Switch is Off"),
        27: Message(
            "Mowing motor overheat",
            "Mow overheat is detected, place mower in base station (27)",
        ),
        28: Message(
            "Check mowing Height", "Mower needs your help, please restart (28)"
        ),
        29: Message(
            "Check mowing Height", "Mower needs your help, please restart (29)"
        ),
        30: Message(
            "No wire signal",
            "Make sure the base station is connected to power supply. Disconnect the power supply and reconnect after 10 seconds. Check connection of the perimeter wire to the base station. Check for breaks in theperimeter wire.",
        ),
        31: Message(
            "Mowing motor overheat", "Mow overheat is detected during manual operation"
        ),
        32: Message(
            "Cross outside", "Please start operation inside the perimeter wire (32)"
        ),
        33: Message("Lift was detected", "Mower needs your help, please restart (33)"),
        34: Message(
            "Inactive time (not in use)",
            "Returning to base station due to inactive time (34)",
        ),
        35: Message(
            "Operation time completed",
            "We reached the required mowing time in the current active zone",
        ),
        37: Message("End of Edge detected"),
        38: Message("Remote button pressed"),
        39: Message("Stop button pressed"),
        41: Message("Lift detection"),
        42: Message("Lift was detected", "Mower needs your help, please restart (42)"),
        43: Message("Mow over-current"),
        44: Message("Stuck In place", "Mower needs your help, please restart (44)"),
        46: Message(
            "Mowing motor overheat",
            "Mow Motor overheating has been detected, place mower in base station (46)",
        ),
        47: Message(
            "No wire signal",
            "Make sure the base station is connected to power supply. Disconnect the power supply and reconnect after 10 seconds. Check connection of the perimeter wire to the base station. Check for breaks in the perimeter wire.",
        ),
        48: Message("End of Edge detected"),
        49: Message("Wrong Menu Place"),
        50: Message("Recharge battery", "Mower needs to be recharged (50)"),
        51: Message("Recharge battery"),
        53: Message("Recharge battery", "Mower needs to be recharged (53)"),
        54: Message("Recharge battery", "Mower needs to be recharged (54)"),
        55: Message("Recharge battery", "Mower needs to be recharged (55)"),
        56: Message("One-time Setup Process"),
        57: Message("Stuck In place", "Mower needs your help, please restart (57)"),
        58: Message("Stop through the App"),
        59: Message("Stuck In place", "Mower needs your help, please restart (59)"),
        60: Message(
            "Mowing motor problem", "Mower needs your help, please restart (60)"
        ),
        61: Message("Maximal Edge quarters"),
        62: Message("Base detected before Entry point"),
        66: Message("Drive over-current"),
        67: Message("Base detected during go to entry point"),
        69: Message(
            "Wait…",
            "Charging operation was stopped in order to send a robot operation GSM message",
        ),
        70: Message("disabling device taken out"),
        71: Message("Stop pressed through the App"),
        72: Message(
            "Please start the operation elsewhere",
            "Mower needs your help, please restart (72)",
        ),
        73: Message("Disabling Device removed"),
        75: Message(
            "No wire signal",
            "Make sure the base station is connected to power supply. Disconnect the power supply and reconnect after 10 seconds. Check connection of the perimeter wire to the base station. Check for breaks in the perimeter wire.",
        ),
        76: Message("Lift problem"),
        77: Message("Skip automatic depart"),
        78: Message("Stop on base station exit"),
        79: Message("Stuck In place", "Mower needs your help, please restart (79)"),
        80: Message("Stuck In place", "Mower needs your help, please restart (80)"),
        81: Message("Lift was detected", "Mower needs your help, please restart (81)"),
        82: Message("Stuck In place", "Mower needs your help, please restart (82)"),
        86: Message("Stuck In place", "Mower needs your help, please restart (86)"),
        87: Message("Lift problem"),
        88: Message("Lift Problem"),
        89: Message(
            "Stuck In place",
            "Mower needs your help, place mower in base station and check charging (89)",
        ),
        90: Message("Slippage Event"),
        91: Message(
            "Help needed; restart in new location",
            "Mower needs your help, please restart (91)",
        ),
        92: Message("Bumper was pressed", "Mower needs your help, please restart (92)"),
        93: Message("Stuck In place", "Mower needs your help, please restart (93)"),
        94: Message(
            "Stuck In place",
            "Mower needs your help, place mower in base station and check charging (94)",
        ),
        95: Message("Bumper was pressed", "Mower needs your help, please restart (95)"),
        98: Message(
            "Help needed; restart in new location",
            "Mower needs your help, please restart (98)",
        ),
        99: Message("Stuck In place", "Mower needs your help, please restart (99)"),
        100: Message(
            "Operation time completed",
            "We reached the required mowing time in the current active zone",
        ),
        101: Message("Stuck In place", "Multiple robot Slippage events are detected."),
        102: Message(
            "Base station pairing required",
            "Mower needs your help, place mower in base station: wait for at least 20 seconds for mower to pair with base station (102)",
        ),
        103: Message(
            "Help needed; restart in new location",
            "Mower needs your help, please restart (103)",
        ),
        104: Message(
            "Help needed; restart in new location",
            "Mower needs your help, please restart (104)",
        ),
        105: Message(
            "Help needed; restart in new location",
            "Mower needs your help, please restart (105)",
        ),
        106: Message(
            "Disabled mode is active",
            "please re-insert the disabling key to continue operation (106)",
        ),
        107: Message("Bumper was pressed", "Body Assembly removed"),
        108: Message("Battery compartment door is open", "Battery door is open"),
        109: Message("charge current problem"),
        110: Message("battery communication problem"),
        111: Message("Battery temperature is too high"),
        112: Message("Help needed; restart in new location"),
        113: Message(
            "Cover is opened",
            "Operation stopped because cover is open. Please close cover to enable operation (113)",
        ),
        114: Message("Place mower in the base station"),
        115: Message("Shunt event"),
        116: Message("Monitor Communication"),
        117: Message("Back docking bumper"),
        118: Message("Back docking failure"),
        119: Message("Max operation time reached"),
        120: Message("Mowing blades are out of balance"),
        127: Message(
            "One-time setup needs to be completed",
            "Your robot must complete the initial setup, to ensure proper functionality",
        ),
        501: Message("Tilt calibration missing"),
        502: Message("Wire calibration failure"),
        503: Message("Mow left thermistor is disconnected"),
        504: Message("Mow right thermistor is disconnected"),
        505: Message("Mow configuration problem"),
        506: Message("Bumper calibration missing"),
        507: Message("Drive motor is disconnected"),
        508: Message("Drive configuration is invalid"),
        509: Message("Tilt calibration failed"),
        510: Message(
            "Tilt calibration failed because accelerometer readings are not in tolerance"
        ),
        511: Message("Accelerometer failure"),
        512: Message("Battery volt calibration failure"),
        513: Message("STOP button is disconnected"),
        515: Message("Safety standard power up test failed"),
        516: Message("Failure #516"),
        517: Message("Mow motor unintentional operation"),
        518: Message("No response from accelerometer device"),
        519: Message("No response from lift sensor"),
        520: Message("Mow motor is disconnected"),
        521: Message("Disabling device readings are invalid"),
        522: Message("lift calibration failure"),
        523: Message("Drive motor odometer failure"),
        524: Message("System configuration failure"),
        525: Message("lift calibration failure"),
        527: Message("Mow motor is disconnected during warming up stage"),
        528: Message("Mow motor left is disconnected"),
        530: Message("controller programming failed"),
        531: Message("monitor programming failed"),
        532: Message("ui programming failed"),
        533: Message("Battery configuration problem"),
        534: Message("Battery communication problem"),
        535: Message("Safety standard event"),
        536: Message("communication problem with monitor processor was detected"),
    }
)

ERROR_MESSAGES: MappingProxyType[int, Message] = MappingProxyType(
    {
        1: Message("Passed", "Operation Passed."),
        2: Message(
            "Operation Failed.", "The Test or Calibration performed has Failed."
        ),
        3: Message("Wait", "Please wait for the process to finish…"),
        4: Message(
            "No Wire Signal",
            "Confirm power supply is plugged into the power outlet. Check power supply and perimeter wire connection to the Base Station. Check the indication on the Base Station.",
        ),
        5: Message("Recharge Battery", "Low battery voltage. Recharge the battery."),
        6: Message(
            "Wheels in The Air",
            "Drive wheels have lost their grip with the ground or the mower is lifted.",
        ),
        7: Message(
            "Key Pressed", "One of the operating panel buttons is constantly pressed."
        ),
        8: Message(
            "Low Temperature",
            "Ambiance temperature is lower than 5ºC (41ºF). The mower will resume automatically.",
        ),
        10: Message(
            "Check Mowing Height",
            "Switch Power Off. Mowing motor is loaded. Check grass height and insure nothing is obstructing the blade rotation.",
        ),
        11: Message(
            "Check Power",
            "Confirm power supply is plugged into the power outlet. Check power supply connection to the Base Station. Check charging contacts.",
        ),
        12: Message(
            "Keep Charged",
            "Keep your mower charged at all times, if it is not being used.",
        ),
        13: Message(
            "Base Problem",
            "The mower is failing to enter the Base Station. Adjust position and clean charging contacts.",
        ),
        14: Message(
            "Start Elsewhere",
            "Check the ground and the drive wheels. Restart elsewhere. If persists, refer to Troubleshooting section of the User Guide.",
        ),
        15: Message(
            "Cross Outside",
            "Some issue was found along the perimeter. Check ground, increase cutting height, or move wire inward.",
        ),
        16: Message(
            "Incorrect Connection",
            "Swap (reverse) the perimeter wire connection at the Base Station.",
        ),
        17: Message(
            "Start Inside", "Place the mower inside the lawn and start it again."
        ),
        18: Message(
            "Stuck in Place",
            "Check ground where stuck and drive wheel rotation is not blocked. Restart elsewhere.",
        ),
        19: Message("Starting Point 1 Problem"),
        20: Message("Starting Point 2 Problem"),
        21: Message("Subzone 3 Entry Problem"),
        22: Message(
            "Lift Calibration Required",
            "Press GO button on the mower to start lift sensor calibration process",
        ),
        23: Message("Base search is disabled"),
        24: Message(
            "Short Operation Time",
            "The actual operation time was shorter than expected.",
        ),
        25: Message(
            "Waiting for Signal…",
            "No signal is detected and operation has stopped. Check all power cable connections. The mower will resume automatically once power is restored.",
        ),
        26: Message(
            "Calibrate Wire Sensor 1", "Turn wire signal 'Off' then press GO."
        ),
        27: Message(
            "Calibrate Wire Sensor 2", "Turn wire signal 'On' then press GO."
        ),
        28: Message(
            "Check Mowing Motor",
            "Switch Power Off. Mowing motor is loaded. Check grass height and insure nothing is obstructing the blade rotation.",
        ),
        31: Message(
            "Learning Edge Distance",
            "Your mower is learning the distance of the Perimeter Wire in a Separated Zone. Press STOP after completing a full circle around the lawn.",
        ),
        34: Message(
            "Test Wire Position",
            "Walk alongside your mower while it is following the edge to test the wire position.",
        ),
        35: Message(
            "Test Edge Mode",
            "Place the mower into the Base Station. Press GO to start. The mower will follow Edge back to Base Station.",
        ),
        36: Message(
            "Test Near Wire Follow",
            "Place mower near the edge. Press OK to start. The mower will follow Edge at maximum Near Wire Follow distance.",
        ),
        37: Message("Demo Mode", "Mower is in Demo Mode."),
        40: Message(
            "Place robot in Base Station",
            "Place the mower into the Base Station before beginning the process of adding a starting point.",
        ),
        41: Message(
            "Alarm will soon Activate.",
            "Press OK to deactivate theft protection alarm.",
        ),
        42: Message(
            "Mow Motor Overheat",
            "The mowing motor has been overloaded for too long. The mower will resume automatically.",
        ),
        43: Message(
            "Mow Overheat",
            "The mowing motor(s) are overheating. Wait for cooldown. Operation will restart automatically.",
        ),
        44: Message("Warning! Motors will now be activated."),
        45: Message(
            "Calibrate Lift Sensor 1", "Place the mower on the ground then press GO"
        ),
        46: Message("Calibrate Lift Sensor 2", "Lift mower then press GO."),
        47: Message(
            "Mower is Lifted",
            "For safety purposes, switch the power off before lifting the mower.",
        ),
        48: Message(
            "Theft protection is active",
            '"It\'s impossible to switch the mower off as long as the theft protection is active."',
        ),
        50: Message(
            "Disabling Device Removed",
            "Insert the Disabling Device to operate the mower",
        ),
        51: Message(
            "Standby Mode",
            "Your mower is currently charging in standby mode. Switch ON for operation.",
        ),
        52: Message(
            "Adjust the Wire",
            "The mower has bumped into something along the edge and backed up. Move the wire slightly inward. Press OK to continue.",
        ),
        60: Message(
            "Intensity Error", "The Intensity set is too high for your lawn area."
        ),
        61: Message(
            "Decrease Inactive Time",
            "Too many Inactive days/hours have been set for your lawn area or Mowing Frequency (Interval) is too high.",
        ),
        62: Message(
            "Alarm will soon Activate.",
            "Press OK to deactivate theft protection alarm.",
        ),
        63: Message(
            "Inactive Hours 2 modified via App",
            'Inactive hours cannot be set via the mower as long as \\"Inactive Hours 2\\" are enabled via the app.',
        ),
        64: Message(
            "No Base Station Found",
            '\\"Searching Base Station\\" operation cannot be performed in a zone without a Base Station.',
        ),
        85: Message(
            "Invalid system configuration",
            "The installed Software and Hardware configurations are not compatible.",
        ),
        86: Message(
            "Waiting for Signal…",
            "No signal is detected and operation has stopped. Check all power cable connections. The mower will resume automatically once power is restored.",
        ),
        87: Message(
            "Mow Motor Overheat",
            "The mowing motor has been overloaded for too long. The mower will resume automatically.",
        ),
        88: Message(
            "Drive Motor Overheat",
            "The drive motor(s) has been overloaded for too long. The mower will resume automatically.",
        ),
        89: Message(
            "Child Lock is activated",
            "To operate your mower, please press GO + STOP together, then select the desired command.",
        ),
        90: Message("Starting Point 1 Problem"),
        91: Message("Starting Point 2 Problem"),
        92: Message("Subzone 3 Entry Problem"),
        93: Message("Subzone 4 Entry Problem"),
        94: Message(
            "Disabling Device Removed",
            "Insert the Disabling Device to operate the mower",
        ),
        95: Message("Rain Sensing…"),
        501: Message("Wire signal off reading is higher than wire signal on reading"),
        502: Message(
            "Wire reading indicates calibration failed because either the signal off amplitude readings or the signal on amplitude readings exceed their tolerance"
        ),
        503: Message(
            "Wire reading indicates calibration failed because we detect that robot is not inside the garden during the calibration with signal on"
        ),
        504: Message(
            "Wire reading indicates calibration failed because we detect that in/out readings are invalid"
        ),
        505: Message(
            "Wire reading indicates calibration failed because the difference between wire max signal threshold and wire amplitude set point is too big"
        ),
        506: Message(
            "Wire reading indicates calibration failed because the wire no signal gain is too small"
        ),
        507: Message(
            "Drive Motor Disconnected",
            "Open mower's cover and check drive motors' connections",
        ),
        508: Message("Drive configuration is invalid"),
        509: Message("Tilt calibration failed"),
        510: Message(
            "Tilt calibration failed because accelerometer readings are not in tolerance"
        ),
        511: Message("Accelerometer failure"),
        512: Message("Battery voltage calibration failure"),
        513: Message("Error 513"),
        514: Message("Error 514"),
        515: Message("Error 515"),
        516: Message("Error 516"),
        517: Message("Error 517"),
        518: Message("Error 518"),
        519: Message("Error 519"),
        520: Message("Error 520"),
        521: Message(
            "Disabling Device Removed",
            "Insert the Disabling Device to operate the mower",
        ),
        522: Message(
            "Lift Calibration Required",
            "Press GO button on the mower to start lift sensor calibration process",
        ),
        525: Message(
            "Lift Calibration Required",
            "Press GO button on the mower to start lift sensor calibration process",
        ),
        527: Message(
            "Mowing Motor Disconnected",
            "Open mower's cover and check mowing motor's connection",
        ),
    }
)

NO_DEPART_MESSAGES: MappingProxyType[int, Message] = MappingProxyType(
    {
        0: Message(title="I'm home"),
        1: Message(title="Charging at home"),
        2: Message(title="I'm home"),
        3: Message(title="Demo mode"),
        4: Message(title="Check the mower", text="Robomow waiting for response"),
        5: Message(
            title="Short operations",
            text="Short operations detected.  Inspect blades and wheels",
        ),
        6: Message(title="I'm home"),
        7: Message(title="I'm home"),
        8: Message(
            title="Can't recharge",
            text="No charging voltage detected. Inspect charging pins",
        ),
        9: Message(
            title="Chilly weather",
            text="Low ambient temperature. Automatic operation paused",
        ),
        10: Message(
            title="Starting point",
            text="The mower was unable to reach the starting point",
        ),
        11: Message(title="Departing soon", text="Departing really soon"),
        12: Message(title="Invalid schedule", text="Invalid weekly schedule settings"),
        13: Message(
            title="Mowing skipped", text="Operation cancelled. Staying home today"
        ),
        14: Message(title="Stand-by mode", text="Mower is switched off in its base"),
        15: Message(
            title="Disabled", text="Disabling device is removed. No operation allowed"
        ),
        16: Message(
            title="Departure delay",
            text="Departure is being delayed for up to 4 hours.",
        ),
        17: Message(
            title="Saving energy",
            text="Energy Saver mode. Automatic departure is disabled",
        ),
    }
)
