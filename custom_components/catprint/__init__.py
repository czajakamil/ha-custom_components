import logging

import aiohttp
import voluptuous as vol
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant, ServiceCall
from homeassistant.helpers.aiohttp_client import async_get_clientsession
import homeassistant.helpers.config_validation as cv

from .const import DOMAIN, CONF_URL
from .coordinator import CatPrintCoordinator

_LOGGER = logging.getLogger(__name__)

PLATFORMS = ["sensor", "notify"]


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    url = entry.data[CONF_URL]
    coordinator = CatPrintCoordinator(hass, url)
    await coordinator.async_config_entry_first_refresh()

    hass.data.setdefault(DOMAIN, {})[entry.entry_id] = coordinator
    await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)
    _register_services(hass, url)
    return True


async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    unloaded = await hass.config_entries.async_unload_platforms(entry, PLATFORMS)
    if unloaded:
        hass.data[DOMAIN].pop(entry.entry_id)
    return unloaded


def _register_services(hass: HomeAssistant, url: str) -> None:
    session = async_get_clientsession(hass)

    async def _post(path: str, payload: dict) -> None:
        try:
            await session.post(
                f"{url}{path}",
                json=payload,
                timeout=aiohttp.ClientTimeout(total=60),
            )
        except Exception as err:
            _LOGGER.error("CatPrint service error (%s): %s", path, err)

    async def handle_print_text(call: ServiceCall) -> None:
        await _post("/api/print/text", {
            "text": call.data["text"],
            "font_size": call.data.get("font_size", 24),
        })

    async def handle_print_shopping_list(call: ServiceCall) -> None:
        await _post("/api/print/ha-shopping-list", {
            "items": call.data["items"],
            "title": call.data.get("title", "Lista zakupów"),
        })

    async def handle_print_notification(call: ServiceCall) -> None:
        await _post("/api/print/ha-notification", {
            "title": call.data["title"],
            "message": call.data["message"],
            "source": call.data.get("source", "Home Assistant"),
        })

    async def handle_print_qr(call: ServiceCall) -> None:
        await _post("/api/print/qr", {
            "data": call.data["data"],
            "caption": call.data.get("caption", ""),
        })

    async def handle_scan(call: ServiceCall) -> None:
        await _post("/api/scan", {})

    async def handle_flush_queue(call: ServiceCall) -> None:
        await _post("/api/queue/flush", {})

    hass.services.async_register(
        DOMAIN, "print_text", handle_print_text,
        schema=vol.Schema({
            vol.Required("text"): cv.string,
            vol.Optional("font_size", default=24): vol.All(int, vol.Range(min=8, max=48)),
        }),
    )
    hass.services.async_register(
        DOMAIN, "print_shopping_list", handle_print_shopping_list,
        schema=vol.Schema({
            vol.Required("items"): vol.All(cv.ensure_list, [cv.string]),
            vol.Optional("title", default="Lista zakupów"): cv.string,
        }),
    )
    hass.services.async_register(
        DOMAIN, "print_notification", handle_print_notification,
        schema=vol.Schema({
            vol.Required("title"): cv.string,
            vol.Required("message"): cv.string,
            vol.Optional("source", default="Home Assistant"): cv.string,
        }),
    )
    hass.services.async_register(
        DOMAIN, "print_qr", handle_print_qr,
        schema=vol.Schema({
            vol.Required("data"): cv.string,
            vol.Optional("caption", default=""): cv.string,
        }),
    )
    hass.services.async_register(DOMAIN, "scan", handle_scan, schema=vol.Schema({}))
    hass.services.async_register(DOMAIN, "flush_queue", handle_flush_queue, schema=vol.Schema({}))
