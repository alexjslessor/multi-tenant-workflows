from fastapi import Request
from fastapi.exceptions import HTTPException

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
