from __future__ import annotations

import aiohttp
import voluptuous as vol

from homeassistant import config_entries
from homeassistant.core import HomeAssistant
from homeassistant.helpers.aiohttp_client import async_get_clientsession

from .api import CookidooTodayApi
from .const import CONF_BASE_URL, CONF_SCAN_INTERVAL, DEFAULT_SCAN_INTERVAL, DOMAIN


async def _validate_input(hass: HomeAssistant, base_url: str) -> None:
    session = async_get_clientsession(hass)
    api = CookidooTodayApi(session, base_url)
    await api.get_today()


class CookidooTodayConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    VERSION = 1

    async def async_step_user(self, user_input: dict | None = None):
        errors: dict[str, str] = {}

        if user_input is not None:
            base_url = user_input[CONF_BASE_URL].rstrip("/")

            await self.async_set_unique_id(base_url)
            self._abort_if_unique_id_configured()

            try:
                await _validate_input(self.hass, base_url)
            except aiohttp.ClientError:
                errors["base"] = "cannot_connect"
            except Exception:
                errors["base"] = "unknown"
            else:
                data = {CONF_BASE_URL: base_url}
                options = {
                    CONF_SCAN_INTERVAL: user_input.get(CONF_SCAN_INTERVAL, DEFAULT_SCAN_INTERVAL),
                }
                return self.async_create_entry(title="Cookidoo Today", data=data, options=options)

        schema = vol.Schema(
            {
                vol.Required(CONF_BASE_URL): str,
                vol.Optional(CONF_SCAN_INTERVAL, default=DEFAULT_SCAN_INTERVAL): vol.Coerce(type(DEFAULT_SCAN_INTERVAL)),
            }
        )
        # Uwaga: UI i tak pokaże sensownie timedelta, ale jak wolisz sekundy,
        # to powiedz, przerobię na int.
        return self.async_show_form(step_id="user", data_schema=schema, errors=errors)

    async def async_step_import(self, user_input: dict):
        return await self.async_step_user(user_input)


class CookidooTodayOptionsFlowHandler(config_entries.OptionsFlow):
    def __init__(self, entry: config_entries.ConfigEntry) -> None:
        self.entry = entry

    async def async_step_init(self, user_input: dict | None = None):
        if user_input is not None:
            return self.async_create_entry(title="", data=user_input)

        schema = vol.Schema(
            {
                vol.Optional(
                    CONF_SCAN_INTERVAL,
                    default=self.entry.options.get(CONF_SCAN_INTERVAL, DEFAULT_SCAN_INTERVAL),
                ): vol.Coerce(type(DEFAULT_SCAN_INTERVAL)),
            }
        )
        return self.async_show_form(step_id="init", data_schema=schema)
