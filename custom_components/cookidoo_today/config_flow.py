from __future__ import annotations

from typing import Any

import voluptuous as vol

from homeassistant import config_entries
from homeassistant.core import HomeAssistant
from homeassistant.helpers.aiohttp_client import async_get_clientsession

from .api import CookidooTodayApi
from .const import (
    DOMAIN,
    CONF_BASE_URL,
    CONF_TODAY_PATH,
    CONF_VERIFY_SSL,
    CONF_TIMEOUT,
    DEFAULT_BASE_URL,
    DEFAULT_TODAY_PATH,
    DEFAULT_VERIFY_SSL,
    DEFAULT_TIMEOUT,
    CannotConnect,
    InvalidResponse,
)


def _normalize_base_url(raw: str) -> str:
    url = (raw or "").strip()
    if not url:
        return url
    if "://" not in url:
        url = "http://" + url
    return url.rstrip("/")


def _normalize_path(raw: str) -> str:
    path = (raw or "").strip()
    if not path:
        return DEFAULT_TODAY_PATH
    if not path.startswith("/"):
        path = "/" + path
    return path


def _validate_user_input(data: dict[str, Any]) -> dict[str, Any]:
    base_url = _normalize_base_url(data[CONF_BASE_URL])
    today_path = _normalize_path(data.get(CONF_TODAY_PATH, DEFAULT_TODAY_PATH))

    timeout = int(data.get(CONF_TIMEOUT, DEFAULT_TIMEOUT))
    if timeout < 3:
        timeout = 3
    if timeout > 120:
        timeout = 120

    return {
        CONF_BASE_URL: base_url,
        CONF_TODAY_PATH: today_path,
        CONF_VERIFY_SSL: bool(data.get(CONF_VERIFY_SSL, True)),
        CONF_TIMEOUT: timeout,
    }


class CookidooTodayConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    VERSION = 1

    async def async_step_user(self, user_input: dict[str, Any] | None = None):
        errors: dict[str, str] = {}

        if user_input is not None:
            cleaned = _validate_user_input(user_input)

            api = CookidooTodayApi(
                session=async_get_clientsession(self.hass),
                base_url=cleaned[CONF_BASE_URL],
                today_path=cleaned[CONF_TODAY_PATH],
                verify_ssl=cleaned[CONF_VERIFY_SSL],
                timeout=cleaned[CONF_TIMEOUT],
            )

            try:
                await api.async_ping()
            except CannotConnect:
                errors["base"] = "cannot_connect"
            except InvalidResponse:
                errors["base"] = "invalid_response"
            except Exception:  # noqa: BLE001
                errors["base"] = "unknown"
            else:
                # unikalność po base_url + today_path (bo możesz mieć kilka różnych endpointów)
                await self.async_set_unique_id(f"{cleaned[CONF_BASE_URL]}|{cleaned[CONF_TODAY_PATH]}")
                self._abort_if_unique_id_configured()

                return self.async_create_entry(
                    title="Cookidoo Today",
                    data=cleaned,
                )

        schema = vol.Schema(
            {
                vol.Required(CONF_BASE_URL, default=DEFAULT_BASE_URL): str,
                vol.Optional(CONF_TODAY_PATH, default=DEFAULT_TODAY_PATH): str,
                vol.Optional(CONF_VERIFY_SSL, default=DEFAULT_VERIFY_SSL): bool,
                vol.Optional(CONF_TIMEOUT, default=DEFAULT_TIMEOUT): int,
            }
        )

        return self.async_show_form(step_id="user", data_schema=schema, errors=errors)

    @staticmethod
    def async_get_options_flow(config_entry: config_entries.ConfigEntry):
        return CookidooTodayOptionsFlow(config_entry)


class CookidooTodayOptionsFlow(config_entries.OptionsFlow):
    def __init__(self, entry: config_entries.ConfigEntry) -> None:
        self.entry = entry

    async def async_step_init(self, user_input: dict[str, Any] | None = None):
        errors: dict[str, str] = {}

        if user_input is not None:
            cleaned = _validate_user_input(user_input)

            api = CookidooTodayApi(
                session=async_get_clientsession(self.hass),
                base_url=cleaned[CONF_BASE_URL],
                today_path=cleaned[CONF_TODAY_PATH],
                verify_ssl=cleaned[CONF_VERIFY_SSL],
                timeout=cleaned[CONF_TIMEOUT],
            )

            try:
                await api.async_ping()
            except CannotConnect:
                errors["base"] = "cannot_connect"
            except InvalidResponse:
                errors["base"] = "invalid_response"
            except Exception:  # noqa: BLE001
                errors["base"] = "unknown"
            else:
                return self.async_create_entry(title="", data=cleaned)

        # domyślne wartości: options -> data -> default
        base_url = self.entry.options.get(CONF_BASE_URL, self.entry.data.get(CONF_BASE_URL, DEFAULT_BASE_URL))
        today_path = self.entry.options.get(CONF_TODAY_PATH, self.entry.data.get(CONF_TODAY_PATH, DEFAULT_TODAY_PATH))
        verify_ssl = self.entry.options.get(CONF_VERIFY_SSL, self.entry.data.get(CONF_VERIFY_SSL, DEFAULT_VERIFY_SSL))
        timeout = self.entry.options.get(CONF_TIMEOUT, self.entry.data.get(CONF_TIMEOUT, DEFAULT_TIMEOUT))

        schema = vol.Schema(
            {
                vol.Required(CONF_BASE_URL, default=base_url): str,
                vol.Optional(CONF_TODAY_PATH, default=today_path): str,
                vol.Optional(CONF_VERIFY_SSL, default=bool(verify_ssl)): bool,
                vol.Optional(CONF_TIMEOUT, default=int(timeout)): int,
            }
        )

        return self.async_show_form(step_id="init", data_schema=schema, errors=errors)
