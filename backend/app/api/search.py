"""Retrieval-only endpoint: see exactly what the search tool would give the model.

Used by the smoke test, by evaluation's retrieval checks, and for debugging a wrong answer:
run the same query here and compare the passages and ranks.
"""

from typing import Annotated

from fastapi import APIRouter, Request
from pydantic import BaseModel, Field, StringConstraints, model_validator

from app.api.auth import Viewer
from app.retrieval.search import SearchFilters, SearchService

router = APIRouter(prefix="/api", tags=["search"])


class SearchRequest(BaseModel):
    query: Annotated[str, StringConstraints(strip_whitespace=True, min_length=1, max_length=500)]
    document_ids: Annotated[list[int] | None, Field(max_length=50)] = None
    page_from: Annotated[int | None, Field(ge=1)] = None
    page_to: Annotated[int | None, Field(ge=1)] = None
    top_k: Annotated[int, Field(ge=1, le=10)] = 8

    @model_validator(mode="after")
    def pages_in_order(self) -> "SearchRequest":
        if self.page_from and self.page_to and self.page_from > self.page_to:
            raise ValueError("page_from must not be after page_to")
        return self


class HitOut(BaseModel):
    chunk_id: int
    document_id: int
    title: str
    page_no: int
    text: str
    score: float
    vector_rank: int | None
    keyword_rank: int | None


class SearchResponse(BaseModel):
    hits: list[HitOut]
    cache: str
    ms: int


@router.post("/search")
async def search(body: SearchRequest, request: Request, user: Viewer) -> SearchResponse:
    service: SearchService = request.app.state.search
    filters = SearchFilters(
        tuple(body.document_ids) if body.document_ids else None,
        body.page_from,
        body.page_to,
        viewer=user,
    )
    result = await service.search(body.query, filters, body.top_k)
    return SearchResponse(
        hits=[HitOut(**{k: getattr(h, k) for k in HitOut.model_fields}) for h in result.hits],
        cache=result.cache,
        ms=result.ms,
    )
