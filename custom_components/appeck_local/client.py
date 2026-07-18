"""TinyTuya client wrapper for APPECK Local."""

from __future__ import annotations

from typing import Any

import tinytuya

from .const import (
    DP_BRIGHTNESS,
    DP_COLOR,
    DP_MODE,
    DP_PIXEL,
    DP_POWER,
    MODE_COLOR,
)


class AppeckClient:
    """Synchronous local client. Call from Home Assistant's executor."""

    def __init__(self, host: str, device_id: str, local_key: str, version: str) -> None:
        self._device = tinytuya.Device(device_id, host, local_key)
        self._device.set_version(float(version))
        self._device.set_socketPersistent(True)
        self._device.set_socketTimeout(5)

    def status(self) -> dict[str, Any]:
        """Return the controller status response."""
        result = self._device.status()
        if not isinstance(result, dict):
            raise ConnectionError(f"Unexpected status response: {result!r}")
        if "Error" in result:
            raise ConnectionError(str(result))
        return result

    def set_dp(self, dp: int, value: Any) -> None:
        """Write one Tuya datapoint and raise on a reported error."""
        result = self._device.set_value(dp, value)
        if isinstance(result, dict) and "Error" in result:
            raise ConnectionError(str(result))

    def set_power(self, enabled: bool) -> None:
        self.set_dp(DP_POWER, enabled)

    def set_brightness(self, brightness: int) -> None:
        self.set_dp(DP_BRIGHTNESS, brightness)

    def set_color(self, encoded_hsv: str) -> None:
        self.set_dp(DP_MODE, MODE_COLOR)
        self.set_dp(DP_COLOR, encoded_hsv)

    def set_pixel_payload(self, payload: str) -> None:
        self.set_dp(DP_PIXEL, payload)
