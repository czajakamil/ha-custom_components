from __future__ import annotations

from typing import Any

from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity import DeviceInfo
from homeassistant.helpers.update_coordinator import CoordinatorEntity
from homeassistant.components.sensor import SensorEntity

from .const import DOMAIN
from .coordinator import CookidooTodayCoordinator


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry, async_add_entities):
    data = hass.data[DOMAIN][entry.entry_id]
    coordinator: CookidooTodayCoordinator = data["coordinator"]

    device = DeviceInfo(
        identifiers={(DOMAIN, entry.entry_id)},
        name="Cookidoo Today",
        manufacturer="Cookidoo",
        model="Cookidoo Today Add-on API",
    )

    async_add_entities(
        [
            CookidooTodayCountSensor(coordinator, entry, device),
            CookidooWeekCountSensor(coordinator, entry, device),
        ]
    )


class _BaseCookidooSensor(CoordinatorEntity[CookidooTodayCoordinator], SensorEntity):
    def __init__(self, coordinator: CookidooTodayCoordinator, entry: ConfigEntry, device: DeviceInfo) -> None:
        super().__init__(coordinator)
        self._entry = entry
        self._device = device

    @property
    def device_info(self) -> DeviceInfo:
        return self._device


class CookidooTodayCountSensor(_BaseCookidooSensor):
    _attr_name = "Cookidoo Today recipes"
    _attr_icon = "mdi:chef-hat"

    @property
    def unique_id(self) -> str:
        return f"{self._entry.entry_id}_today_recipes_count"

    @property
    def native_value(self) -> int:
        today = (self.coordinator.data or {}).get("today", {})  # type: ignore[assignment]
        recipes = today.get("recipes", []) if isinstance(today, dict) else []
        return len(recipes)

    @property
    def extra_state_attributes(self) -> dict[str, Any]:
        today = (self.coordinator.data or {}).get("today", {})
        if not isinstance(today, dict):
            return {}
        return {
            "date": today.get("date"),
            "recipes": today.get("recipes", []),
        }


class CookidooWeekCountSensor(_BaseCookidooSensor):
    _attr_name = "Cookidoo Week recipes"
    _attr_icon = "mdi:calendar-week"

    @property
    def unique_id(self) -> str:
        return f"{self._entry.entry_id}_week_recipes_count"

    @property
    def native_value(self) -> int:
        week = (self.coordinator.data or {}).get("week", {})
        if not isinstance(week, dict):
            return 0
        days = week.get("days", [])
        if not isinstance(days, list):
            return 0
        return sum(len(d.get("recipes", [])) for d in days if isinstance(d, dict))

    @property
    def extra_state_attributes(self) -> dict[str, Any]:
        week = (self.coordinator.data or {}).get("week", {})
        if not isinstance(week, dict):
            return {}
        return {"week": week}
