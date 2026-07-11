"""
Zentraler WebSocket-Manager.
Ermöglicht das gleichzeitige Streamen von Telemetrie-, Satelliten- und
Sprachassistenten-Events an beliebig viele verbundene Dashboards
(z.B. mehrere Browser-Tabs oder das Handy-Widget gleichzeitig).
"""
from __future__ import annotations
import asyncio
from typing import Dict, Set
from fastapi import WebSocket
from loguru import logger


class ConnectionManager:
    def __init__(self) -> None:
        # Kanäle: "telemetry", "satellites", "assistant", "search"
        self._channels: Dict[str, Set[WebSocket]] = {}
        self._lock = asyncio.Lock()

    async def connect(self, channel: str, websocket: WebSocket) -> None:
        await websocket.accept()
        async with self._lock:
            self._channels.setdefault(channel, set()).add(websocket)
        logger.info(f"Client verbunden auf Kanal '{channel}'")

    async def disconnect(self, channel: str, websocket: WebSocket) -> None:
        async with self._lock:
            if channel in self._channels:
                self._channels[channel].discard(websocket)

    async def broadcast(self, channel: str, message: dict) -> None:
        dead: list[WebSocket] = []
        for ws in self._channels.get(channel, set()):
            try:
                await ws.send_json(message)
            except Exception:
                dead.append(ws)
        for ws in dead:
            await self.disconnect(channel, ws)


manager = ConnectionManager()
