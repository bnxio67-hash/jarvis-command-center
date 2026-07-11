"""
Das 'Gehirn' von JARVIS: nimmt Text (aus STT) entgegen, entscheidet via
Claude Tool-Calling, ob Tools ausgeführt werden müssen, führt sie aus,
und liefert eine finale, für TTS optimierte deutsche Antwort zurück.
"""
from __future__ import annotations
from anthropic import AsyncAnthropic
from app.core.config import get_settings
from app.agents.tools import TOOL_SCHEMAS, execute_tool
from app.models.schemas import ChatResponse

settings = get_settings()
client = AsyncAnthropic(api_key=settings.ANTHROPIC_API_KEY)

SYSTEM_PROMPT = """\
Du bist JARVIS, ein persönlicher KI-Assistent für ein Android Command Center.
Antworte immer auf Deutsch, präzise, sachlich, mit einem Hauch trockenem Humor.
Antworten müssen für Sprachausgabe (TTS) geeignet sein: keine Markdown-Formatierung,
kurze klare Sätze, keine Aufzählungszeichen.
Nutze die verfügbaren Tools, wenn eine Anfrage aktuelle Daten
(Telemetrie, Websuche, Satellitenposition) erfordert.
"""


async def process_command(text: str, session_id: str = "default") -> ChatResponse:
    messages: list[dict] = [{"role": "user", "content": text}]
    tool_calls_log: list[dict] = []

    # Tool-Calling-Loop: max. 5 Runden gegen Endlosschleifen
    for _ in range(5):
        response = await client.messages.create(
            model=settings.LLM_MODEL,
            max_tokens=1024,
            system=SYSTEM_PROMPT,
            tools=TOOL_SCHEMAS,
            messages=messages,
        )

        if response.stop_reason != "tool_use":
            final_text = "".join(
                block.text for block in response.content if block.type == "text"
            )
            return ChatResponse(reply_text=final_text, tool_calls=tool_calls_log)

        # Assistant-Turn (inkl. tool_use Blöcke) an History anhängen
        messages.append({"role": "assistant", "content": response.content})

        tool_results = []
        for block in response.content:
            if block.type != "tool_use":
                continue
            result = await execute_tool(block.name, block.input)
            tool_calls_log.append({"name": block.name, "input": block.input, "result": result})
            tool_results.append(
                {
                    "type": "tool_result",
                    "tool_use_id": block.id,
                    "content": str(result),
                }
            )

        messages.append({"role": "user", "content": tool_results})

    return ChatResponse(
        reply_text="Ich konnte die Anfrage nicht abschließend verarbeiten, zu viele Tool-Aufrufe.",
        tool_calls=tool_calls_log,
    )
