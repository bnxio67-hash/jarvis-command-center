"""
Tool-Definitionen für das zentrale KI-Gehirn (Anthropic Tool-Calling Format).
Jedes Tool hier ist eine Brücke zu einem der anderen Module
(Telemetrie, Web-Suche, Satelliten-Tracking, Smartphone-Aktionen).

Neue Fähigkeiten hinzufügen = hier ein neues Tool-Schema + Handler eintragen.
"""
from __future__ import annotations
from typing import Any, Awaitable, Callable
from app.services.telemetry_store import telemetry_store
from app.services.search_service import run_web_search

# ---- 1. Tool-Schemas (was das LLM sieht) -----------------------------------

TOOL_SCHEMAS: list[dict[str, Any]] = [
    {
        "name": "get_phone_telemetry",
        "description": (
            "Liefert die aktuellsten Hardware-Werte des Smartphones: "
            "CPU-Auslastung pro Kern, RAM-Verbrauch, Akkustand und Netzwerkgeschwindigkeit."
        ),
        "input_schema": {"type": "object", "properties": {}},
    },
    {
        "name": "web_search",
        "description": (
            "Durchsucht das Internet nach aktuellen Informationen (Nachrichten, Preise, Fakten) "
            "und liefert eine kompakte, für Sprachausgabe geeignete Zusammenfassung auf Deutsch."
        ),
        "input_schema": {
            "type": "object",
            "properties": {
                "query": {"type": "string", "description": "Suchanfrage in natürlicher Sprache"},
                "max_results": {"type": "integer", "default": 5},
            },
            "required": ["query"],
        },
    },
    {
        "name": "get_satellite_position",
        "description": (
            "Gibt die aktuelle Position eines Satelliten (z.B. ISS) als Länge/Breite/Höhe zurück, "
            "basierend auf den zuletzt geladenen TLE-Daten."
        ),
        "input_schema": {
            "type": "object",
            "properties": {
                "satellite_name": {"type": "string", "description": "z.B. 'ISS (ZARYA)'"},
            },
            "required": ["satellite_name"],
        },
    },
]

# ---- 2. Tool-Handler (was tatsächlich ausgeführt wird) ---------------------

async def _handle_get_phone_telemetry(_: dict[str, Any]) -> dict[str, Any]:
    latest = telemetry_store.get_latest()
    if latest is None:
        return {"error": "Noch keine Telemetriedaten vom Smartphone empfangen."}
    return latest.model_dump()


async def _handle_web_search(args: dict[str, Any]) -> dict[str, Any]:
    result = await run_web_search(args["query"], args.get("max_results", 5))
    return result.model_dump()


async def _handle_get_satellite_position(args: dict[str, Any]) -> dict[str, Any]:
    # Platzhalter: wird in Modul 2 (Satelliten-Service) implementiert
    # und dann hier via satellite_service.get_position(...) angebunden.
    return {
        "note": (
            f"Satelliten-Live-Tracking für '{args['satellite_name']}' wird über den "
            "CesiumJS-Frontend-Service berechnet (siehe Modul 2)."
        )
    }


TOOL_HANDLERS: dict[str, Callable[[dict[str, Any]], Awaitable[dict[str, Any]]]] = {
    "get_phone_telemetry": _handle_get_phone_telemetry,
    "web_search": _handle_web_search,
    "get_satellite_position": _handle_get_satellite_position,
}


async def execute_tool(name: str, tool_input: dict[str, Any]) -> dict[str, Any]:
    handler = TOOL_HANDLERS.get(name)
    if handler is None:
        return {"error": f"Unbekanntes Tool: {name}"}
    return await handler(tool_input)
