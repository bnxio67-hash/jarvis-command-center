from fastapi import APIRouter, Depends
from app.core.security import verify_api_key
from app.core.ws_manager import manager
from app.models.schemas import ChatRequest, ChatResponse
from app.agents.brain import process_command

router = APIRouter(prefix="/api/chat", tags=["Chat & Sprachsteuerung"])


@router.post("/command", response_model=ChatResponse, dependencies=[Depends(verify_api_key)])
async def handle_command(payload: ChatRequest) -> ChatResponse:
    """
    Nimmt den per Speech-to-Text transkribierten Text vom Handy entgegen
    (ausgelöst durch das Wake-Word 'Jarvis'), lässt ihn vom KI-Gehirn
    verarbeiten und gibt eine TTS-fertige Antwort zurück.
    """
    response = await process_command(payload.text, payload.session_id)

    # Live an alle verbundenen Dashboards pushen (z.B. für Chat-Verlauf-Anzeige)
    await manager.broadcast(
        "assistant",
        {"type": "command_processed", "input": payload.text, "output": response.reply_text},
    )
    return response
