"""Config flow for Cookidoo Today."""
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
    CONF_SCAN_INTERVAL,
    DEFAULT_SCAN_INTERVAL,
)

_LOGGER = logging.getLogger(__name__)

ERROR_CANNOT_CONNECT = "cannot_connect"
ERROR_INVALID_URL = "invalid_url"
ERROR_UNKNOWN = "unknown"


def _normalize_base_url(value: str) -> str:
    """Normalize and validate base URL."""
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

    if not url.scheme or not url.host:
        raise vol.Invalid("Invalid URL")

    return str(url)


async def _async_validate_addon(hass: HomeAssistant, base_url: str) -> None:
    """Validate connection to the FastAPI addon."""
    session = async_get_clientsession(hass)

    # FastAPI standard endpoint; doesn't require you to add a custom /health.
    test_url = f"{base_url}/openapi.json"

    try:
        async with asyncio.timeout(10):
            resp = await session.get(test_url)
            await resp.release()
    except (TimeoutError, aiohttp.ClientError) as err:
        _LOGGER.debug("Cannot connect to %s: %s", test_url, err)
        raise ConnectionError from err

    # 200 = OK. 401/403 could happen if someone puts auth in front, still "reachable".
    if resp.status in (200, 401, 403):
        return

    if resp.status == 404:
        raise ValueError("Not a FastAPI endpoint (openapi.json not found)")

    if resp.status >= 500:
        raise ConnectionError

    # Anything else: treat as invalid-ish
    raise ValueError(f"Unexpected status: {resp.status}")


class CookidooTodayConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    """Handle config flow for Cookidoo Today."""
    VERSION = 1

    async def async_step_user(self, user_input: dict[str, Any] | None = None):
        errors: dict[str, str] = {}

        if user_input is not None:
            base_url = user_input[CONF_BASE_URL]

            # Avoid duplicates by base_url
            await self.async_set_unique_id(base_url)
            self._abort_if_unique_id_configured()

            try:
                await _async_validate_addon(self.hass, base_url)
            except ValueError:
                errors["base"] = ERROR_INVALID_URL
            except ConnectionError:
                errors["base"] = ERROR_CANNOT_CONNECT
            except Exception:  # noqa: BLE001
                _LOGGER.exception("Unexpected error during config flow")
                errors["base"] = ERROR_UNKNOWN
            else:
                title = URL(base_url).host or "Cookidoo Today"
                return self.async_create_entry(title=title, data={CONF_BASE_URL: base_url})

        schema = vol.Schema(
            {
                vol.Required(CONF_BASE_URL, default=DEFAULT_BASE_URL): _normalize_base_url,
            }
        )

        return self.async_show_form(step_id="user", data_schema=schema, errors=errors)

    @staticmethod
    def async_get_options_flow(config_entry: config_entries.ConfigEntry):
        return CookidooTodayOptionsFlowHandler(config_entry)


class CookidooTodayOptionsFlowHandler(config_entries.OptionsFlow):
    """Handle options for Cookidoo Today."""

    def __init__(self, config_entry: config_entries.ConfigEntry) -> None:
        self.config_entry = config_entry

    async def async_step_init(self, user_input: dict[str, Any] | None = None):
        errors: dict[str, str] = {}

        current_base_url = (
            self.config_entry.options.get(CONF_BASE_URL)
            or self.config_entry.data.get(CONF_BASE_URL)
            or DEFAULT_BASE_URL
        )
        current_scan = self.config_entry.options.get(CONF_SCAN_INTERVAL, DEFAULT_SCAN_INTERVAL)

        if user_input is not None:
            base_url = user_input[CONF_BASE_URL]

            try:
                await _async_validate_addon(self.hass, base_url)
            except ValueError:
                errors["base"] = ERROR_INVALID_URL
            except ConnectionError:
                errors["base"] = ERROR_CANNOT_CONNECT
            except Exception:  # noqa: BLE001
                _LOGGER.exception("Unexpected error during options flow")
                errors["base"] = ERROR_UNKNOWN
            else:
                # Keep base_url also in options so user can override later
                return self.async_create_entry(title="", data=user_input)

        schema = vol.Schema(
            {
                vol.Required(CONF_BASE_URL, default=current_base_url): _normalize_base_url,
                vol.Required(CONF_SCAN_INTERVAL, default=current_scan): vol.Coerce(int),
            }
        )
        return self.async_show_form(step_id="init", data_schema=schema, errors=errors)
