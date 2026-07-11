"""
Hält die zuletzt empfangenen Telemetriedaten im Speicher, damit sowohl
das Dashboard (WebSocket) als auch das Tool-Calling (get_phone_telemetry)
darauf zugreifen können, ohne jedes Mal eine Datenbank abzufragen.
"""
from __future__ import annotations
from app.models.schemas import TelemetryPayload


class TelemetryStore:
    def __init__(self) -> None:
        self._latest: dict[str, TelemetryPayload] = {}

    def update(self, payload: TelemetryPayload) -> None:
        self._latest[payload.device_id] = payload

    def get_latest(self, device_id: str | None = None) -> TelemetryPayload | None:
        if device_id:
            return self._latest.get(device_id)
        if not self._latest:
            return None
        # Ohne device_id: den zuletzt aktualisierten Eintrag zurückgeben
        return list(self._latest.values())[-1]


telemetry_store = TelemetryStore()
