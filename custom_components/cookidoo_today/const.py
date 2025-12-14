from homeassistant.const import Platform

DOMAIN = "cookidoo_today"

CONF_BASE_URL = "base_url"
DEFAULT_BASE_URL = "http://127.0.0.1:8099"

CONF_SCAN_INTERVAL = "scan_interval"
DEFAULT_SCAN_INTERVAL = 15

PLATFORMS: list[Platform] = [Platform.SENSOR]
