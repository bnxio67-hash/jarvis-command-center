from fastapi import APIRouter, Depends
from app.core.security import verify_api_key
from app.models.schemas import SearchRequest, SearchResponse
from app.services.search_service import run_web_search

router = APIRouter(prefix="/api/search", tags=["Autonome Suche"])


@router.post("/query", response_model=SearchResponse, dependencies=[Depends(verify_api_key)])
async def search(payload: SearchRequest) -> SearchResponse:
    return await run_web_search(payload.query, payload.max_results)
