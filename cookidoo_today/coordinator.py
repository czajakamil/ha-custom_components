from __future__ import annotations

import logging
from datetime import timedelta
import aiohttp

from homeassistant.core import HomeAssistant
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator, UpdateFailed

from .api import CookidooTodayApi
from .const import DOMAIN

_LOGGER = logging.getLogger(__name__)


class CookidooTodayCoordinator(DataUpdateCoordinator[dict]):
    def __init__(
        self,
        hass: HomeAssistant,
        api: CookidooTodayApi,
        update_interval: timedelta,
    ) -> None:
        super().__init__(
            hass,
            _LOGGER,
            name=DOMAIN,
            update_interval=update_interval,
        )
        self.api = api

    async def _async_update_data(self) -> dict:
        try:
            today = await self.api.get_today()
            week = await self.api.get_week()
            return {"today": today, "week": week}
        except aiohttp.ClientError as err:
            raise UpdateFailed(f"API error: {err}") from err
        except Exception as err:
            raise UpdateFailed(f"Unexpected error: {err}") from err
