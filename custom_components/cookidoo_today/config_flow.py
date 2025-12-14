from __future__ import annotations

from typing import Any

import aiohttp
import voluptuous as vol

from homeassistant import config_entries
from homeassistant.config_entries import ConfigFlowResult, OptionsFlowWithReload
from homeassistant.core import callback
from homeassistant.helpers.aiohttp_client import async_get_clientsession
from homeassistant.helpers.selector import selector

from .api import CookidooTodayApi
from .const import (
    DOMAIN,
    CONF_BASE_URL,
    CONF_EMAIL,
    CONF_PASSWORD,
    CONF_COUNTRY,
    CONF_REFRESH_MINUTES,
    DEFAULT_BASE_URL,
    DEFAULT_COUNTRY,
    DEFAULT_REFRESH_MINUTES,
)


async def _validate_api(hass, base_url: str) -> None:
    """Sprawdź czy API żyje i odpowiada."""
    session = async_get_clientsession(hass)
    api = CookidooTodayApi(session, base_url)
    await api.get_today()


STEP_USER_SCHEMA = vol.Schema(
    {
        vol.Required(CONF_BASE_URL, default=DEFAULT_BASE_URL): selector(
            {"text": {"type": "text"}}
        ),
        vol.Required(CONF_EMAIL): selector({"text": {"type": "email"}}),
        vol.Required(CONF_PASSWORD): selector({"text": {"type": "password"}}),
        vol.Optional(CONF_COUNTRY, default=DEFAULT_COUNTRY): selector(
            {"text": {"type": "text"}}
        ),
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
        vol.Optional(CONF_COUNTRY, default=DEFAULT_COUNTRY): selector(
            {"text": {"type": "text"}}
        ),
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
    """Config flow for Cookidoo Today."""

    VERSION = 1

    async def async_step_user(
        self, user_input: dict[str, Any] | None = None
    ) -> ConfigFlowResult:
        errors: dict[str, str] = {}

        if user_input is not None:
            base_url = str(user_input[CONF_BASE_URL]).rstrip("/")
            email = str(user_input[CONF_EMAIL]).strip()
            password = str(user_input[CONF_PASSWORD])

            # Unique ID: per endpoint API (żeby nie dodać dwa razy tego samego)
            await self.async_set_unique_id(base_url)
            self._abort_if_unique_id_configured()

            try:
                await _validate_api(self.hass, base_url)
            except aiohttp.ClientResponseError as err:
                # 401/403 -> traktuj jako invalid_auth (jeśli kiedyś API będzie autoryzowane)
                if err.status in (401, 403):
                    errors["base"] = "invalid_auth"
                else:
                    errors["base"] = "cannot_connect"
            except aiohttp.ClientError:
                errors["base"] = "cannot_connect"
            except Exception:
                errors["base"] = "unknown"
            else:
                # data = wrażliwe (email/hasło), options = ustawienia
                return self.async_create_entry(
                    title="Cookidoo Today",
                    data={
                        CONF_BASE_URL: base_url,
                        CONF_EMAIL: email,
                        CONF_PASSWORD: password,
                    },
                    options={
                        CONF_COUNTRY: user_input.get(CONF_COUNTRY, DEFAULT_COUNTRY),
                        CONF_REFRESH_MINUTES: int(
                            user_input.get(CONF_REFRESH_MINUTES, DEFAULT_REFRESH_MINUTES)
                        ),
                    },
                )

        return self.async_show_form(
            step_id="user",
            data_schema=STEP_USER_SCHEMA,
            errors=errors,
        )

    @staticmethod
    @callback
    def async_get_options_flow(
        config_entry: config_entries.ConfigEntry,
    ) -> config_entries.OptionsFlow:
        return CookidooTodayOptionsFlow()


class CookidooTodayOptionsFlow(OptionsFlowWithReload):
    """Options flow with automatic reload after save."""

    async def async_step_init(
        self, user_input: dict[str, Any] | None = None
    ) -> ConfigFlowResult:
        if user_input is not None:
            # Normalizacja typów
            user_input[CONF_REFRESH_MINUTES] = int(
                user_input.get(CONF_REFRESH_MINUTES, DEFAULT_REFRESH_MINUTES)
            )
            if CONF_COUNTRY in user_input and user_input[CONF_COUNTRY] is not None:
                user_input[CONF_COUNTRY] = str(user_input[CONF_COUNTRY]).strip()

            return self.async_create_entry(title="", data=user_input)

        schema = self.add_suggested_values_to_schema(
            OPTIONS_SCHEMA, self.config_entry.options
        )
        return self.async_show_form(step_id="init", data_schema=schema)
