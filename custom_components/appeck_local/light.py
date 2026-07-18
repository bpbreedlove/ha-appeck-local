"""Light platform for APPECK Local."""

from __future__ import annotations

import asyncio
from typing import Any

import voluptuous as vol

from homeassistant.components.light import (
    ATTR_BRIGHTNESS,
    ATTR_HS_COLOR,
    ColorMode,
    LightEntity,
    LightEntityFeature,
)
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import CONF_STATE, STATE_OFF, STATE_ON
from homeassistant.core import HomeAssistant
from homeassistant.helpers import config_validation as cv
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from .client import AppeckClient
from .const import (
    CONF_BULB_COUNT,
    CONF_DEVICE_ID,
    DP_BRIGHTNESS,
    DP_COLOR,
    DP_POWER,
)
from .protocol import encode_pixel_hsv, encode_pixel_off, encode_tuya_hsv

ATTR_PIXELS = "pixels"
ATTR_HUE = "hue"
ATTR_SATURATION = "saturation"
ATTR_VALUE = "value"

SET_PIXELS_SCHEMA = {
    vol.Required(ATTR_PIXELS): vol.All(cv.ensure_list, [vol.Coerce(int)]),
    vol.Optional(CONF_STATE, default=STATE_ON): vol.In([STATE_ON, STATE_OFF]),
    vol.Optional(ATTR_HUE, default=0): vol.All(vol.Coerce(int), vol.Range(min=0, max=360)),
    vol.Optional(ATTR_SATURATION, default=1000): vol.All(
        vol.Coerce(int), vol.Range(min=0, max=1000)
    ),
    vol.Optional(ATTR_VALUE, default=1000): vol.All(
        vol.Coerce(int), vol.Range(min=0, max=1000)
    ),
}


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry[AppeckClient],
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up the APPECK light entity."""
    entity = AppeckLight(entry)
    async_add_entities([entity], True)

    platform = entity.platform
    platform.async_register_entity_service(
        "set_pixels",
        SET_PIXELS_SCHEMA,
        "async_set_pixels",
    )


class AppeckLight(LightEntity):
    """Representation of one APPECK permanent-light controller."""

    _attr_has_entity_name = True
    _attr_name = "Permanent Lights"
    _attr_color_mode = ColorMode.HS
    _attr_supported_color_modes = {ColorMode.HS}
    _attr_supported_features = LightEntityFeature.EFFECT
    _attr_should_poll = True

    def __init__(self, entry: ConfigEntry[AppeckClient]) -> None:
        self._entry = entry
        self._client = entry.runtime_data
        self._bulb_count = entry.data[CONF_BULB_COUNT]
        self._attr_unique_id = entry.data[CONF_DEVICE_ID]
        self._attr_device_info = {
            "identifiers": {("appeck_local", entry.data[CONF_DEVICE_ID])},
            "name": entry.title,
            "manufacturer": "APPECK / Tuya",
            "model": "Permanent Outdoor Lights Pro",
        }
        self._attr_is_on = False
        self._attr_brightness = 255
        self._attr_hs_color = (0.0, 100.0)

    async def async_update(self) -> None:
        """Poll device state."""
        response = await self.hass.async_add_executor_job(self._client.status)
        dps: dict[str, Any] = response.get("dps", {})
        self._attr_is_on = bool(dps.get(str(DP_POWER), dps.get(DP_POWER, False)))

        raw_brightness = dps.get(str(DP_BRIGHTNESS), dps.get(DP_BRIGHTNESS))
        if isinstance(raw_brightness, int):
            self._attr_brightness = round(max(0, min(1000, raw_brightness)) * 255 / 1000)

        raw_color = dps.get(str(DP_COLOR), dps.get(DP_COLOR))
        if isinstance(raw_color, str) and len(raw_color) >= 12:
            try:
                hue = int(raw_color[0:4], 16)
                saturation = int(raw_color[4:8], 16)
                self._attr_hs_color = (float(hue), saturation / 10)
            except ValueError:
                pass

    async def async_turn_on(self, **kwargs: Any) -> None:
        """Turn on the string and optionally apply color or brightness."""
        hs_color = kwargs.get(ATTR_HS_COLOR)
        brightness = kwargs.get(ATTR_BRIGHTNESS)

        await self.hass.async_add_executor_job(self._client.set_power, True)

        if brightness is not None:
            tuya_brightness = max(0, min(1000, round(brightness * 1000 / 255)))
            await self.hass.async_add_executor_job(
                self._client.set_brightness, tuya_brightness
            )
            self._attr_brightness = brightness

        if hs_color is not None:
            hue = round(hs_color[0])
            saturation = round(hs_color[1] * 10)
            value = max(1, round((brightness or self._attr_brightness or 255) * 1000 / 255))
            encoded = encode_tuya_hsv(hue, saturation, value)
            await self.hass.async_add_executor_job(self._client.set_color, encoded)
            self._attr_hs_color = hs_color

        self._attr_is_on = True
        self.async_write_ha_state()

    async def async_turn_off(self, **kwargs: Any) -> None:
        """Turn off the entire light string."""
        await self.hass.async_add_executor_job(self._client.set_power, False)
        self._attr_is_on = False
        self.async_write_ha_state()

    async def async_set_pixels(
        self,
        pixels: list[int],
        state: str = STATE_ON,
        hue: int = 0,
        saturation: int = 1000,
        value: int = 1000,
    ) -> None:
        """Apply a DP61 command to one or more addressed pixels."""
        for pixel in pixels:
            if state == STATE_OFF:
                payload = encode_pixel_off(self._bulb_count, pixel)
            else:
                payload = encode_pixel_hsv(
                    self._bulb_count,
                    pixel,
                    hue,
                    saturation,
                    value,
                )
            await self.hass.async_add_executor_job(
                self._client.set_pixel_payload, payload
            )
            await asyncio.sleep(0.075)
