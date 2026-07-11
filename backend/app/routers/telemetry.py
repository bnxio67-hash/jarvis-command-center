from fastapi import APIRouter, Depends, WebSocket, WebSocketDisconnect
from app.core.security import verify_api_key
from app.core.ws_manager import manager
from app.models.schemas import TelemetryPayload
from app.services.telemetry_store import telemetry_store

router = APIRouter(tags=["Telemetrie"])


@router.post("/api/telemetry/ingest", dependencies=[Depends(verify_api_key)])
async def ingest_telemetry(payload: TelemetryPayload) -> dict:
    """
    Empfängt im Sekundentakt Hardware-Daten vom Android-Bridge-Skript (Modul 4)
    und leitet sie live per WebSocket an alle Dashboards weiter.
    """
    telemetry_store.update(payload)
    await manager.broadcast("telemetry", payload.model_dump())
    return {"status": "ok"}


@router.websocket("/ws/telemetry")
async def telemetry_ws(websocket: WebSocket) -> None:
    """Dashboard verbindet sich hierüber, um Live-Telemetrie zu empfangen."""
    await manager.connect("telemetry", websocket)
    try:
        while True:
            await websocket.receive_text()  # Keep-Alive / Ping vom Client
    except WebSocketDisconnect:
        await manager.disconnect("telemetry", websocket)
