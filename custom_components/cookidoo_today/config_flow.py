"""Config flow for Cookidoo Today integration."""

from __future__ import annotations

import asyncio
import logging
from typing import Any

import aiohttp
import voluptuous as vol
from yarl import URL

from homeassistant import config_entries
from homeassistant.core import HomeAssistant
from homeassistant.helpers.aiohttp_client import async_get_clientsession

from .const import (
    DOMAIN,
    CONF_BASE_URL,
    DEFAULT_BASE_URL,
)

_LOGGER = logging.getLogger(__name__)

# Błędy, które pokażą się w UI (translations możesz dodać później)
ERROR_CANNOT_CONNECT = "cannot_connect"
ERROR_INVALID_URL = "invalid_url"
ERROR_UNKNOWN = "unknown"


def _normalize_base_url(value: str) -> str:
    """Normalize and validate base URL.

    Accepts:
    - https://host:port
    - http://host:port
    - host:port  (dopisze http://)
    - host       (dopisze http://)
    """
    if not isinstance(value, str):
        raise vol.Invalid("Not a string")

    raw = value.strip()
    if not raw:
        raise vol.Invalid("Empty")

    if not raw.startswith(("http://", "https://")):
        raw = f"http://{raw}"

    raw = raw.rstrip("/")

    try:
        url = URL(raw)
    except Exception as err:
        raise vol.Invalid("Invalid URL") from err

    # Minimalna sensowność
    if not url.scheme or not url.host:
        raise vol.Invalid("Invalid URL")

    return str(url)


async def _async_validate_input(hass: HomeAssistant, base_url: str) -> None:
    """Validate the provided base URL by doing a lightweight HTTP request."""
    session = async_get_clientsession(hass)

    # Tu robimy “ping” na root. Jak masz endpoint /health, podmień path na "/health".
    test_url = f"{base_url}/"

    try:
        async with asyncio.timeout(10):
            resp = await session.get(test_url)
            # Nie czytamy body, bo to tylko test łączności
            await resp.release()
    except (TimeoutError, aiohttp.ClientError) as err:
        _LOGGER.debug("Cannot connect to %s: %s", test_url, err)
        raise ConnectionError from err

    # 401/403 niekoniecznie musi być błędem (może chronisz endpoint),
    # ale 404 też może oznaczać, że URL jest zły. Przyjmijmy prostą logikę:
    if resp.status >= 500:
        raise ConnectionError
    if resp.status == 404:
        raise ValueError("Not found")


class CookidooTodayConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    """Handle a config flow for Cookidoo Today."""

    VERSION = 1

    async def async_step_user(self, user_input: dict[str, Any] | None = None):
        """Handle the initial step."""
        errors: dict[str, str] = {}

        if user_input is not None:
            base_url = user_input[CONF_BASE_URL]

            # Unikalność: nie pozwól dodać tej samej instancji dwa razy
            await self.async_set_unique_id(base_url)
            self._abort_if_unique_id_configured()

            try:
                await _async_validate_input(self.hass, base_url)
            except ValueError:
                errors["base"] = ERROR_INVALID_URL
            except ConnectionError:
                errors["base"] = ERROR_CANNOT_CONNECT
            except Exception:  # noqa: BLE001
                _LOGGER.exception("Unexpected error during config flow")
                errors["base"] = ERROR_UNKNOWN
            else:
                title = URL(base_url).host or "Cookidoo Today"
                return self.async_create_entry(title=title, data=user_input)

        schema = vol.Schema(
            {
                vol.Required(CONF_BASE_URL, default=DEFAULT_BASE_URL): _normalize_base_url,
            }
        )

        return self.async_show_form(step_id="user", data_schema=schema, errors=errors)

    async def async_step_reauth(self, user_input: dict[str, Any] | None = None):
        """Handle reauth (if you ever need it)."""
        # Zachowujemy referencję do wpisu, który się “psuje”
        self._reauth_entry = self.hass.config_entries.async_get_entry(
            self.context["entry_id"]
        )
        return await self.async_step_reauth_confirm()

    async def async_step_reauth_confirm(self, user_input: dict[str, Any] | None = None):
        """Confirm reauth."""
        errors: dict[str, str] = {}

        if user_input is not None:
            base_url = user_input[CONF_BASE_URL]

            try:
                await _async_validate_input(self.hass, base_url)
            except ValueError:
                errors["base"] = ERROR_INVALID_URL
            except ConnectionError:
                errors["base"] = ERROR_CANNOT_CONNECT
            except Exception:  # noqa: BLE001
                _LOGGER.exception("Unexpected error during reauth")
                errors["base"] = ERROR_UNKNOWN
            else:
                # Aktualizujemy data we wpisie (Home Assistant to wspiera)
                self.hass.config_entries.async_update_entry(
                    self._reauth_entry,
                    data={**self._reauth_entry.data, CONF_BASE_URL: base_url},
                )
                await self.hass.config_entries.async_reload(self._reauth_entry.entry_id)
                return self.async_abort(reason="reauth_successful")

        current = (
            self._reauth_entry.data.get(CONF_BASE_URL, DEFAULT_BASE_URL)
            if hasattr(self, "_reauth_entry") and self._reauth_entry
            else DEFAULT_BASE_URL
        )

        schema = vol.Schema(
            {
                vol.Required(CONF_BASE_URL, default=current): _normalize_base_url,
            }
        )

        return self.async_show_form(
            step_id="reauth_confirm",
            data_schema=schema,
            errors=errors,
        )

    @staticmethod
    def async_get_options_flow(config_entry: config_entries.ConfigEntry):
        """Get the options flow handler."""
        return CookidooTodayOptionsFlowHandler(config_entry)


class CookidooTodayOptionsFlowHandler(config_entries.OptionsFlow):
    """Handle options for Cookidoo Today."""

    def __init__(self, config_entry: config_entries.ConfigEntry) -> None:
        self.config_entry = config_entry

    async def async_step_init(self, user_input: dict[str, Any] | None = None):
        """Manage the options."""
        errors: dict[str, str] = {}

        if user_input is not None:
            base_url = user_input[CONF_BASE_URL]

            try:
                await _async_validate_input(self.hass, base_url)
            except ValueError:
                errors["base"] = ERROR_INVALID_URL
            except ConnectionError:
                errors["base"] = ERROR_CANNOT_CONNECT
            except Exception:  # noqa: BLE001
                _LOGGER.exception("Unexpected error during options")
                errors["base"] = ERROR_UNKNOWN
            else:
                # Options zapisujemy w options, nie w data
                return self.async_create_entry(title="", data=user_input)

        current = (
            self.config_entry.options.get(CONF_BASE_URL)
            or self.config_entry.data.get(CONF_BASE_URL)
            or DEFAULT_BASE_URL
        )

        schema = vol.Schema(
            {
                vol.Required(CONF_BASE_URL, default=current): _normalize_base_url,
            }
        )

        return self.async_show_form(step_id="init", data_schema=schema, errors=errors)
