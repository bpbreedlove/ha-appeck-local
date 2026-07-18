"""Config flow for APPECK Local."""

from __future__ import annotations

from typing import Any

import voluptuous as vol

from homeassistant import config_entries
from homeassistant.const import CONF_HOST
from homeassistant.core import HomeAssistant

from .client import AppeckClient
from .const import (
    CONF_BULB_COUNT,
    CONF_DEVICE_ID,
    CONF_LOCAL_KEY,
    CONF_PROTOCOL_VERSION,
    DEFAULT_BULB_COUNT,
    DEFAULT_PROTOCOL_VERSION,
    DOMAIN,
)


async def _validate_input(hass: HomeAssistant, data: dict[str, Any]) -> None:
    client = AppeckClient(
        host=data[CONF_HOST],
        device_id=data[CONF_DEVICE_ID],
        local_key=data[CONF_LOCAL_KEY],
        version=data[CONF_PROTOCOL_VERSION],
    )
    await hass.async_add_executor_job(client.status)


class AppeckLocalConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    """Handle an APPECK Local config flow."""

    VERSION = 1

    async def async_step_user(self, user_input: dict[str, Any] | None = None):
        """Handle the initial setup step."""
        errors: dict[str, str] = {}

        if user_input is not None:
            await self.async_set_unique_id(user_input[CONF_DEVICE_ID])
            self._abort_if_unique_id_configured()
            try:
                await _validate_input(self.hass, user_input)
            except Exception:  # Home Assistant surfaces a generic connection error.
                errors["base"] = "cannot_connect"
            else:
                return self.async_create_entry(
                    title=f"APPECK {user_input[CONF_HOST]}",
                    data=user_input,
                )

        schema = vol.Schema(
            {
                vol.Required(CONF_HOST): str,
                vol.Required(CONF_DEVICE_ID): str,
                vol.Required(CONF_LOCAL_KEY): str,
                vol.Required(
                    CONF_PROTOCOL_VERSION,
                    default=DEFAULT_PROTOCOL_VERSION,
                ): vol.In(["3.3", "3.4", "3.5"]),
                vol.Required(
                    CONF_BULB_COUNT,
                    default=DEFAULT_BULB_COUNT,
                ): vol.All(vol.Coerce(int), vol.Range(min=1, max=255)),
            }
        )
        return self.async_show_form(
            step_id="user",
            data_schema=schema,
            errors=errors,
        )
