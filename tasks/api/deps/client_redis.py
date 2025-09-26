from fastapi import Request
from fastapi.exceptions import HTTPException

async def client_redis(
    request: Request,
):
    try:
        return request.app.state.redis_client
    except (Exception) as e:
        raise HTTPException(
            status_code=404,
            detail=f"Redis not available: {str(e)}",
        )