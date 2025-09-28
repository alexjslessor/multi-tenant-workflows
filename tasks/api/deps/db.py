import redis
from fastapi import Request
from fastapi.exceptions import HTTPException
from collections.abc import AsyncGenerator
from sqlalchemy.ext.asyncio import (
    AsyncSession, 
)


async def get_async_session(
    request: Request,
) -> AsyncGenerator[AsyncSession, None]:
    async with request.app.state.async_session_maker() as session:
        yield session

async def redis_client(
    request: Request,
) -> redis.Redis:
    try:
        return request.app.state.redis_client
    except (Exception) as e:
        raise HTTPException(
            status_code=404,
            detail=f"Redis not available: {str(e)}",
        )

async def get_channel(
    request: Request,
):
    try:
        return request.app.state.rabbit_channel
    except (Exception):
        raise HTTPException(
            status_code=404,
            detail="RabbitMQ channel not available",
        )