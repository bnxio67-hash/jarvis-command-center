"""
Einfache, aber wirksame API-Key-Absicherung.
Das Handy schickt den Key im Header 'X-API-Key' mit jeder Anfrage.
"""
from fastapi import Header, HTTPException, status
from app.core.config import get_settings

settings = get_settings()


async def verify_api_key(x_api_key: str = Header(...)) -> None:
    if x_api_key != settings.API_KEY:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Ungültiger oder fehlender API-Key.",
        )
