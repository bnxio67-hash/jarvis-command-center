"""
Autonomer Such-Agent (Grundgerüst).
Volle Implementierung inkl. BeautifulSoup-Parsing und Such-API-Anbindung
folgt in Modul 3 als eigenständige Datei; hier die Schnittstelle,
die vom Tool-Calling (Modul 1) bereits genutzt werden kann.
"""
from __future__ import annotations
import httpx
from app.core.config import get_settings
from app.models.schemas import SearchResponse, SearchResultItem

settings = get_settings()


async def run_web_search(query: str, max_results: int = 5) -> SearchResponse:
    """
    Führt eine Websuche aus und liefert kompakte, deutsche Ergebnisse.
    Aktuell als Platzhalter mit Brave-Search-kompatiblem Aufbau -
    echten API-Key in .env unter SEARCH_API_KEY eintragen.
    """
    if not settings.SEARCH_API_KEY:
        return SearchResponse(
            query=query,
            spoken_summary=(
                "Es ist noch kein Such-API-Schlüssel konfiguriert. "
                "Bitte SEARCH_API_KEY in der .env-Datei setzen."
            ),
            results=[],
        )

    async with httpx.AsyncClient(timeout=10) as client:
        resp = await client.get(
            "https://api.search.brave.com/res/v1/web/search",
            params={"q": query, "count": max_results},
            headers={"X-Subscription-Token": settings.SEARCH_API_KEY},
        )
        resp.raise_for_status()
        data = resp.json()

    items = [
        SearchResultItem(
            title=r.get("title", ""),
            url=r.get("url", ""),
            summary=r.get("description", ""),
        )
        for r in data.get("web", {}).get("results", [])[:max_results]
    ]

    spoken = (
        f"Ich habe {len(items)} Ergebnisse zu '{query}' gefunden. "
        f"Das relevanteste: {items[0].title}." if items
        else f"Ich habe leider keine Ergebnisse zu '{query}' gefunden."
    )

    return SearchResponse(query=query, spoken_summary=spoken, results=items)
