from __future__ import annotations

from datetime import timedelta
from homeassistant.const import Platform

DOMAIN = "cookidoo_today"

CONF_BASE_URL = "base_url"
CONF_TODAY_PATH = "today_path"
CONF_VERIFY_SSL = "verify_ssl"
CONF_TIMEOUT = "timeout"

DEFAULT_BASE_URL = "http://a0d7b954-cookidoo_today:8000"
DEFAULT_TODAY_PATH = "/today"
DEFAULT_VERIFY_SSL = True
DEFAULT_TIMEOUT = 10

SCAN_INTERVAL = timedelta(minutes=15)

PLATFORMS: list[Platform] = [Platform.SENSOR]


class CookidooTodayError(Exception):
    """Base error for the integration."""


class CannotConnect(CookidooTodayError):
    """Raised when we cannot connect to the backend."""


class InvalidResponse(CookidooTodayError):
    """Raised when backend returns unexpected response."""
