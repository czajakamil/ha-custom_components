from __future__ import annotations

from typing import Any

import voluptuous as vol

from homeassistant import config_entries
from homeassistant.config_entries import ConfigFlowResult, OptionsFlowWithReload
from homeassistant.core import callback
from homeassistant.helpers.selector import selector

from .const import (
    DOMAIN,
    CONF_EMAIL,
    CONF_PASSWORD,
    CONF_COUNTRY,
    CONF_REFRESH_MINUTES,
    DEFAULT_COUNTRY,
    DEFAULT_REFRESH_MINUTES,
)

STEP_USER_SCHEMA = vol.Schema(
    {
        vol.Required(CONF_EMAIL): selector({"text": {"type": "email"}}),
        vol.Required(CONF_PASSWORD): selector({"text": {"type": "password"}}),
        vol.Optional(CONF_COUNTRY, default=DEFAULT_COUNTRY): selector({"text": {"type": "text"}}),
        vol.Optional(CONF_REFRESH_MINUTES, default=DEFAULT_REFRESH_MINUTES): selector(
            {
                "number": {
                    "min": 1,
                    "max": 1440,
                    "mode": "box",
                    "unit_of_measurement": "min",
                }
            }
        ),
    }
)

OPTIONS_SCHEMA = vol.Schema(
    {
        vol.Optional(CONF_COUNTRY, default=DEFAULT_COUNTRY): selector({"text": {"type": "text"}}),
        vol.Optional(CONF_REFRESH_MINUTES, default=DEFAULT_REFRESH_MINUTES): selector(
            {
                "number": {
                    "min": 1,
                    "max": 1440,
                    "mode": "box",
                    "unit_of_measurement": "min",
                }
            }
        ),
    }
)


class CookidooTodayConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    VERSION = 1

    async def async_step_user(self, user_input: dict[str, Any] | None = None) -> ConfigFlowResult:
        if user_input is not None:
            return self.async_create_entry(
                title="Cookidoo Today",
                data={
                    CONF_EMAIL: user_input[CONF_EMAIL],
                    CONF_PASSWORD: user_input[CONF_PASSWORD],
                },
                options={
                    CONF_COUNTRY: user_input.get(CONF_COUNTRY, DEFAULT_COUNTRY),
                    CONF_REFRESH_MINUTES: int(
                        user_input.get(CONF_REFRESH_MINUTES, DEFAULT_REFRESH_MINUTES)
                    ),
                },
            )

        return self.async_show_form(step_id="user", data_schema=STEP_USER_SCHEMA)

    @staticmethod
    @callback
    def async_get_options_flow(config_entry: config_entries.ConfigEntry) -> config_entries.OptionsFlow:
        return CookidooTodayOptionsFlow()


class CookidooTodayOptionsFlow(OptionsFlowWithReload):
    async def async_step_init(self, user_input: dict[str, Any] | None = None) -> ConfigFlowResult:
        if user_input is not None:
            user_input[CONF_REFRESH_MINUTES] = int(
                user_input.get(CONF_REFRESH_MINUTES, DEFAULT_REFRESH_MINUTES)
            )
            return self.async_create_entry(data=user_input)

        schema = self.add_suggested_values_to_schema(OPTIONS_SCHEMA, self.config_entry.options)
        return self.async_show_form(step_id="init", data_schema=schema)
