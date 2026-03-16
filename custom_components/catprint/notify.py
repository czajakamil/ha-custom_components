import logging

import aiohttp
from homeassistant.components.notify import BaseNotificationService, ATTR_DATA
from homeassistant.helpers.aiohttp_client import async_get_clientsession

from .const import CONF_URL

_LOGGER = logging.getLogger(__name__)


async def async_get_service(hass, config, discovery_info=None):
    if discovery_info is None:
        return None
    return CatPrintNotificationService(hass, discovery_info[CONF_URL])


class CatPrintNotificationService(BaseNotificationService):
    def __init__(self, hass, url: str) -> None:
        self.hass = hass
        self.url = url

    async def async_send_message(self, message: str = "", **kwargs) -> None:
        data = kwargs.get(ATTR_DATA) or {}
        font_size = data.get("font_size", 24)
        session = async_get_clientsession(self.hass)
        try:
            await session.post(
                f"{self.url}/api/print/text",
                json={"text": message, "font_size": font_size},
                timeout=aiohttp.ClientTimeout(total=60),
            )
        except Exception as err:
            _LOGGER.error("CatPrint notify failed: %s", err)
