from typing import Any
from pydantic import BaseModel, Field, ValidationError
from fastapi import HTTPException
from fastapi.exceptions import (
    RequestValidationError, 
    ResponseValidationError
)

class BaseCustomException(Exception):
    def __init__(self, message: str):
        self.message = message
        super().__init__(self.message)

    def __repr__(self):
        return f"{self.__class__.__name__}({self.message!r})"

    def __str__(self):
        return f"{self.message}"

class LifespanError(BaseCustomException):
    def __init__(self, message: str):
        self.message = message
        super().__init__(self.message)


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


def parse_validation_error(excp: ValidationError):
    import re
    pattern = re.compile(r"-> (?P<field>\w+)\n\s+.*\(type=(?P<error_type>[\w.]+)\)")
    matches = pattern.finditer(str(excp))
    errors = {}
    for match in matches:
        field = match.group('field')
        errors[field] = 'Missing or In-correct value'
    return ', '.join([f'{k}: {v}' for k, v in errors.items()])

def parse_request_validation_error(excp: RequestValidationError):
    return ' - '.join([f"{i['loc'][1]}: {i['msg']}" for i in excp.errors()])

def parse_response_validation_error(excp: ResponseValidationError):
    try:
        return ' '.join([f"{i['loc'][2]}: {i['msg']}" for i in excp.errors()])
    except (IndexError, AttributeError) as e:
        msg = (
                'ResponseValidationError: '
                'could not parse e.errors() to create response message: '
        )
        # logger.debug(msg)
        raise Exception(msg)

class PostException(HTTPException):
    def __init__(
        self, 
        detail: str, 
        status_code: int
    ):
        super().__init__(
            status_code=status_code, 
            detail=detail
        )

class FrontendException(HTTPException):
    def __init__(
        self,  
        detail: str,
        error: Any,
        status_code: int,
        color: str = 'info',
    ):
        self.error = str(error)
        self.color = color

        super().__init__(
            status_code=status_code, 
            detail=detail
        )