from __future__ import annotations

import aiohttp


class CookidooTodayApi:
    def __init__(self, session: aiohttp.ClientSession, base_url: str) -> None:
        self._session = session
        self._base_url = base_url.rstrip("/")

    async def _get(self, path: str, *, accept: str | None = None) -> aiohttp.ClientResponse:
        url = f"{self._base_url}{path}"
        headers = {}
        if accept:
            headers["Accept"] = accept
        resp = await self._session.get(url, headers=headers)
        resp.raise_for_status()
        return resp

    async def get_today(self) -> dict:
        async with await self._get("/api/today", accept="application/json") as resp:
            return await resp.json()

    async def get_week(self) -> dict:
        async with await self._get("/api/week", accept="application/json") as resp:
            return await resp.json()

    async def get_today_jpg(self) -> bytes:
        async with await self._get("/api/today.jpg", accept="image/jpeg") as resp:
            return await resp.read()

    async def get_week_jpg(self) -> bytes:
        async with await self._get("/api/week.jpg", accept="image/jpeg") as resp:
            return await resp.read()
