from pydantic import BaseModel, Field
from fastapi import Query

class BaseParams(BaseModel):
    limit: int = Field(
        ..., 
        default_factory=lambda: 10)

class JobBody(BaseParams):
    search: list[str] = Field(
        default=['ozempic', 'oxycontin'], 
        description='Comma separated list of keywords to search for')

class ListRedditParams(BaseModel):
    keyword: str | None = Field(
        None,
        description="Optional keyword to filter Reddit posts"
    )

async def pagination(
    skip: int = Query(0, ge=0),
    limit: int = Query(0, ge=0)
) -> tuple[int, int]:
    capped_limit = min(100, limit)
    return (skip, capped_limit)