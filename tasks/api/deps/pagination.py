

from fastapi import Query


async def pagination(
    skip: int = Query(
        0, 
        ge=0),
    limit: int = Query(
        100, 
        ge=0, 
        description='Returns default of 100 but not more than 200'),
) -> tuple[int, int]:
    capped_limit = min(200, limit)
    return (
        skip, 
        capped_limit,
    )