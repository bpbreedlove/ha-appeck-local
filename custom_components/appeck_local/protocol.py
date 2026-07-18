"""Protocol helpers for APPECK/Tuya permanent lights."""

from __future__ import annotations

import base64


def _u16(value: int) -> bytes:
    if not 0 <= value <= 0xFFFF:
        raise ValueError(f"value out of range for uint16: {value}")
    return value.to_bytes(2, "big")


def encode_tuya_hsv(hue: int, saturation: int, value: int) -> str:
    """Encode the DP24 Tuya HSV value as a 12-character hexadecimal string."""
    if not 0 <= hue <= 360:
        raise ValueError("hue must be between 0 and 360")
    if not 0 <= saturation <= 1000:
        raise ValueError("saturation must be between 0 and 1000")
    if not 0 <= value <= 1000:
        raise ValueError("value must be between 0 and 1000")
    return f"{hue:04x}{saturation:04x}{value:04x}"


def encode_pixel_hsv(
    bulb_count: int,
    pixel: int,
    hue: int,
    saturation: int,
    value: int,
) -> str:
    """Build a Base64 DP61 packet that applies HSV to one pixel.

    Confirmed packet layout:
    00 01 [COUNT:2] 01 [HUE:2] [SAT:2] [VAL:2] 81 [PIXEL:1]
    """
    _validate_pixel(bulb_count, pixel)
    payload = (
        b"\x00\x01"
        + _u16(bulb_count)
        + b"\x01"
        + _u16(hue)
        + _u16(saturation)
        + _u16(value)
        + b"\x81"
        + bytes([pixel])
    )
    return base64.b64encode(payload).decode("ascii")


def encode_pixel_off(bulb_count: int, pixel: int) -> str:
    """Build a Base64 DP61 packet that disables one pixel.

    Confirmed packet layout:
    00 01 [COUNT:2] 02 00 00 00 00 00 00 81 [PIXEL:1]
    """
    _validate_pixel(bulb_count, pixel)
    payload = (
        b"\x00\x01"
        + _u16(bulb_count)
        + b"\x02"
        + b"\x00\x00\x00\x00\x00\x00"
        + b"\x81"
        + bytes([pixel])
    )
    return base64.b64encode(payload).decode("ascii")


def _validate_pixel(bulb_count: int, pixel: int) -> None:
    if not 1 <= bulb_count <= 255:
        raise ValueError("bulb_count must be between 1 and 255")
    if not 1 <= pixel <= bulb_count:
        raise ValueError(f"pixel must be between 1 and {bulb_count}")
