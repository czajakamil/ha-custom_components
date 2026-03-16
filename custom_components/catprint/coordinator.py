import logging
from datetime import timedelta

import aiohttp
from homeassistant.helpers.aiohttp_client import async_get_clientsession
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator, UpdateFailed

from .const import DOMAIN, SCAN_INTERVAL_SECONDS

_LOGGER = logging.getLogger(__name__)


class CatPrintCoordinator(DataUpdateCoordinator):
    def __init__(self, hass, url: str) -> None:
        super().__init__(
            hass,
            _LOGGER,
            name=DOMAIN,
            update_interval=timedelta(seconds=SCAN_INTERVAL_SECONDS),
        )
        self.url = url
        self._session = async_get_clientsession(hass)

    async def _async_update_data(self) -> dict:
        timeout = aiohttp.ClientTimeout(total=10)
        try:
            resp = await self._session.get(f"{self.url}/api/status", timeout=timeout)
            resp.raise_for_status()
            data = await resp.json()
        except Exception as err:
            raise UpdateFailed(f"Cannot reach CatPrint at {self.url}: {err}") from err

        try:
            q_resp = await self._session.get(
                f"{self.url}/api/queue",
                params={"status": "pending"},
                timeout=aiohttp.ClientTimeout(total=5),
            )
            queue = await q_resp.json()
            data["pending_jobs"] = len(queue)
        except Exception:
            data["pending_jobs"] = 0

        return data
