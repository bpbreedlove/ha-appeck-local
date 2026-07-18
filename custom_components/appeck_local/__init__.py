"""APPECK Local integration."""

from __future__ import annotations

from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant

from .client import AppeckClient
from .const import (
    CONF_DEVICE_ID,
    CONF_LOCAL_KEY,
    CONF_PROTOCOL_VERSION,
    DOMAIN,
    PLATFORMS,
)


type AppeckConfigEntry = ConfigEntry[AppeckClient]


async def async_setup_entry(hass: HomeAssistant, entry: AppeckConfigEntry) -> bool:
    """Set up APPECK Local from a config entry."""
    client = AppeckClient(
        host=entry.data["host"],
        device_id=entry.data[CONF_DEVICE_ID],
        local_key=entry.data[CONF_LOCAL_KEY],
        version=entry.data[CONF_PROTOCOL_VERSION],
    )
    await hass.async_add_executor_job(client.status)
    entry.runtime_data = client
    await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)
    return True


async def async_unload_entry(hass: HomeAssistant, entry: AppeckConfigEntry) -> bool:
    """Unload a config entry."""
    return await hass.config_entries.async_unload_platforms(entry, PLATFORMS)
