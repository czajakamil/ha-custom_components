from __future__ import annotations

from typing import Any

from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator, UpdateFailed

from .api import CookidooTodayApi
from .const import DOMAIN, SCAN_INTERVAL, CannotConnect, InvalidResponse


class CookidooTodayCoordinator(DataUpdateCoordinator[dict[str, Any]]):
    def __init__(self, hass: HomeAssistant, api: CookidooTodayApi, entry: ConfigEntry) -> None:
        super().__init__(
            hass=hass,
            logger=__import__("logging").getLogger(__name__),
            name=DOMAIN,
            update_interval=SCAN_INTERVAL,
        )
        self.api = api
        self.entry = entry

    async def _async_update_data(self) -> dict[str, Any]:
        try:
            return await self.api.async_get_today()
        except (CannotConnect, InvalidResponse) as e:
            raise UpdateFailed(str(e)) from e
