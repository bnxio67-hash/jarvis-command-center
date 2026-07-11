from fastapi import APIRouter, WebSocket, WebSocketDisconnect
from app.core.ws_manager import manager

router = APIRouter(tags=["Satelliten-Tracking"])


@router.websocket("/ws/satellites")
async def satellites_ws(websocket: WebSocket) -> None:
    """
    Kanal für Live-Satellitenpositionen. Die eigentliche TLE-Berechnung
    läuft im CesiumJS-Frontend (Modul 2, satellite.js / CesiumJS Track-API);
    dieser Kanal dient als optionaler Server-seitiger Broadcast-Punkt,
    z.B. um mehrere Dashboards zu synchronisieren.
    """
    await manager.connect("satellites", websocket)
    try:
        while True:
            await websocket.receive_text()
    except WebSocketDisconnect:
        await manager.disconnect("satellites", websocket)
