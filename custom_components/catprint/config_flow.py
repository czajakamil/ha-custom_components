import aiohttp
import voluptuous as vol
from homeassistant import config_entries
from homeassistant.helpers.aiohttp_client import async_get_clientsession

from .const import DOMAIN, CONF_URL, DEFAULT_URL


class CatPrintConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    VERSION = 1

    async def async_step_user(self, user_input=None):
        errors = {}

        if user_input is not None:
            url = user_input[CONF_URL].rstrip("/")
            try:
                session = async_get_clientsession(self.hass)
                resp = await session.get(
                    f"{url}/api/status",
                    timeout=aiohttp.ClientTimeout(total=10),
                )
                resp.raise_for_status()
                return self.async_create_entry(title="CatPrint", data={CONF_URL: url})
            except Exception:
                errors["base"] = "cannot_connect"

        return self.async_show_form(
            step_id="user",
            data_schema=vol.Schema({
                vol.Required(CONF_URL, default=DEFAULT_URL): str,
            }),
            errors=errors,
        )
