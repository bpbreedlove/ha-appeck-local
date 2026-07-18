"""Tests for confirmed APPECK payload encoders."""

import base64

from custom_components.appeck_local.protocol import (
    encode_pixel_hsv,
    encode_pixel_off,
    encode_tuya_hsv,
)


def test_encode_tuya_hsv() -> None:
    assert encode_tuya_hsv(306, 1000, 1000) == "013203e803e8"


def test_encode_pixel_49_hsv() -> None:
    payload = encode_pixel_hsv(60, 49, 306, 1000, 1000)
    assert payload == "AAEAPAEBMgPoA+iBMQ=="
    assert base64.b64decode(payload).hex() == "0001003c01013203e803e88131"


def test_encode_pixel_49_off() -> None:
    payload = encode_pixel_off(60, 49)
    assert base64.b64decode(payload).hex() == "0001003c020000000000008131"
