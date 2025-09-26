from typing import Any
from fastapi import HTTPException
from pydantic import BaseModel, Field

class ErrorSchema(BaseModel):
    message: str | None = Field(
        default_factory=lambda: '', 
        description='Developer written message. May be displayed to the user on frontend.')
    error: str | None = Field(
        default_factory=lambda: '', 
        description='System generated message, usually from an exception. Always logged.')
    color: str | None = Field(
        default_factory=lambda: '', 
        description='Color for frontend developer user feedback.')
    class Config:
        populate_by_name = True
        json_schema_extra = {
            "examples": [
                {
                    "message": "Developer error msg ",
                    "error": "Exception error msg",
                    "color": "red",
                }
            ]
        }

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

class FrontendException(HTTPException):
    def __init__(
        self,  
        detail: str,
        error: Any,
        status_code: int,
        color: str = 'info',
    ):
        self.detail = detail
        self.error = str(error)
        self.status_code = status_code
        self.color = color
        super().__init__(
            status_code=self.status_code, 
            detail=self.detail
        )