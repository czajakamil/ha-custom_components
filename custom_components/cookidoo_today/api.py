from __future__ import annotations

import asyncio
from dataclasses import dataclass
from typing import Any

import aiohttp

from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.aiohttp_client import async_get_clientsession

from .const import (
    CONF_BASE_URL,
    CONF_TIMEOUT,
    CONF_TODAY_PATH,
    CONF_VERIFY_SSL,
    DEFAULT_TIMEOUT,
    DEFAULT_TODAY_PATH,
    CannotConnect,
    InvalidResponse,
)


def _join_url(base_url: str, path: str) -> str:
    base = base_url.rstrip("/")
    p = "/" + path.lstrip("/")
    return f"{base}{p}"


@dataclass(slots=True)
class CookidooTodayApi:
    session: aiohttp.ClientSession
    base_url: str
    today_path: str
    verify_ssl: bool
    timeout: int

    @classmethod
    def from_entry(cls, hass: HomeAssistant, entry: ConfigEntry) -> "CookidooTodayApi":
        data = entry.data
        opts = entry.options

        base_url = (opts.get(CONF_BASE_URL) or data.get(CONF_BASE_URL) or "").strip()
        today_path = (opts.get(CONF_TODAY_PATH) or data.get(CONF_TODAY_PATH) or DEFAULT_TODAY_PATH).strip()
        verify_ssl = bool(opts.get(CONF_VERIFY_SSL, data.get(CONF_VERIFY_SSL, True)))
        timeout = int(opts.get(CONF_TIMEOUT, data.get(CONF_TIMEOUT, DEFAULT_TIMEOUT)))

        return cls(
            session=async_get_clientsession(hass),
            base_url=base_url,
            today_path=today_path,
            verify_ssl=verify_ssl,
            timeout=timeout,
        )

    async def async_ping(self) -> None:
        """Light connectivity check."""
        # Zakładamy, że endpoint /today istnieje. Jak nie, user zmieni today_path w Options.
        await self.async_get_today()

    async def async_get_today(self) -> dict[str, Any]:
        url = _join_url(self.base_url, self.today_path)

        try:
            async with asyncio.timeout(self.timeout):
                async with self.session.get(url, ssl=self.verify_ssl) as resp:
                    if resp.status >= 400:
                        raise CannotConnect(f"HTTP {resp.status} for {url}")
                    try:
                        data = await resp.json(content_type=None)
                    except Exception as e:  # noqa: BLE001
                        raise InvalidResponse(f"Non-JSON response from {url}") from e
        except (asyncio.TimeoutError, aiohttp.ClientError) as e:
            raise CannotConnect(str(e)) from e

        if not isinstance(data, dict):
            raise InvalidResponse("Expected JSON object (dict).")

        return data
