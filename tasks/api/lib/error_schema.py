from typing import Any
from api_lib.lib import ErrorSchema


responses: dict[int | str, dict[str, Any]] | None = {
    200: {
        "description": "Success"
    },
    400: {
        "model": ErrorSchema,
        "description": "Bad Request Error"
    },
    404: {
        "model": ErrorSchema,
        "description": "Not Found Error"
    },
    422: {
        "model": ErrorSchema,
        "description": "Unprocessable Entity Error"
    },
    500: {
        "model": ErrorSchema,
        "description": "Internal Server Error"
    }
}