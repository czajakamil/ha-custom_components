from __future__ import annotations

from datetime import timedelta
from homeassistant.const import Platform

DOMAIN = "cookidoo_today"

CONF_BASE_URL = "base_url"
CONF_SCAN_INTERVAL = "scan_interval"

DEFAULT_SCAN_INTERVAL = timedelta(minutes=5)

PLATFORMS: list[Platform] = [Platform.SENSOR, Platform.CAMERA]
