from homeassistant.components.sensor import SensorEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .const import DOMAIN
from .coordinator import CatPrintCoordinator


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    coordinator: CatPrintCoordinator = hass.data[DOMAIN][entry.entry_id]
    async_add_entities([
        CatPrintStatusSensor(coordinator, entry),
        CatPrintQueueSensor(coordinator, entry),
    ])


class CatPrintStatusSensor(CoordinatorEntity, SensorEntity):
    _attr_name = "CatPrint Status"
    _attr_icon = "mdi:printer"

    def __init__(self, coordinator: CatPrintCoordinator, entry: ConfigEntry) -> None:
        super().__init__(coordinator)
        self._attr_unique_id = f"{entry.entry_id}_status"

    @property
    def native_value(self) -> str:
        if self.coordinator.data:
            return self.coordinator.data.get("printer", {}).get("status", "unknown")
        return "unavailable"

    @property
    def extra_state_attributes(self) -> dict:
        if not self.coordinator.data:
            return {}
        p = self.coordinator.data.get("printer", {})
        return {
            "printer_name": p.get("name"),
            "address": p.get("address"),
            "print_count": p.get("print_count"),
            "last_print": p.get("last_print"),
            "error": p.get("error"),
        }


class CatPrintQueueSensor(CoordinatorEntity, SensorEntity):
    _attr_name = "CatPrint Pending Jobs"
    _attr_icon = "mdi:printer-alert"
    _attr_native_unit_of_measurement = "jobs"

    def __init__(self, coordinator: CatPrintCoordinator, entry: ConfigEntry) -> None:
        super().__init__(coordinator)
        self._attr_unique_id = f"{entry.entry_id}_pending_jobs"

    @property
    def native_value(self) -> int | None:
        if self.coordinator.data:
            return self.coordinator.data.get("pending_jobs", 0)
        return None
