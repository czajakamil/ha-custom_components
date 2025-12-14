from __future__ import annotations

from typing import Any

from homeassistant.components.sensor import SensorEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity import DeviceInfo
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .const import DOMAIN
from .coordinator import CookidooTodayCoordinator


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry, async_add_entities) -> None:
    coordinator: CookidooTodayCoordinator = hass.data[DOMAIN][entry.entry_id]
    async_add_entities([CookidooTodaySensor(coordinator, entry)])


class CookidooTodaySensor(CoordinatorEntity[CookidooTodayCoordinator], SensorEntity):
    _attr_has_entity_name = True
    _attr_name = "Today"

    def __init__(self, coordinator: CookidooTodayCoordinator, entry: ConfigEntry) -> None:
        super().__init__(coordinator)
        self._entry = entry
        self._attr_unique_id = f"{entry.entry_id}_today"

    @property
    def device_info(self) -> DeviceInfo:
        return DeviceInfo(
            identifiers={(DOMAIN, self._entry.entry_id)},
            name="Cookidoo Today",
            manufacturer="czajakamil",
            model="Backend API",
        )

    @property
    def native_value(self) -> str | None:
        data = self.coordinator.data or {}
        # Spróbuj sensownie wyciągnąć tytuł (fallbacki, bo backendy bywają… kreatywne)
        for key in ("title", "name"):
            if isinstance(data.get(key), str) and data[key].strip():
                return data[key].strip()

        recipe = data.get("recipe")
        if isinstance(recipe, dict):
            for key in ("title", "name"):
                if isinstance(recipe.get(key), str) and recipe[key].strip():
                    return recipe[key].strip()

        # Jak nic nie ma, nie kłam. HA pokaże "unknown".
        return None

    @property
    def extra_state_attributes(self) -> dict[str, Any]:
        data = self.coordinator.data or {}
        # Atrybuty jako pełny JSON (jak Cię to zacznie boleć, potem się to przytnie)
        return {"raw": data}
