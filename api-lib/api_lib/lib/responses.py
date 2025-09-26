from typing import Any
from fastapi import HTTPException
from fastapi.exceptions import RequestValidationError, ResponseValidationError
from pydantic import ValidationError

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
        self.status_code = status_code
        self.detail = detail

class FrontendException(HTTPException):
    def __init__(
        self, 
        message: Any, 
        error: Any,
        status_code: int = 404,
        color: str = 'warning'
    ):
        self.message = message
        self.error = str(error)
        self.status_code = status_code
        self.color = color
        self.detail = self.message

    @classmethod
    def from_error(
        cls, 
        message, 
        error, 
        status_code: int = 404
    ):
        return cls(
            message=message,
            error=error,
            status_code=status_code,
            color='error'
        )

    @classmethod
    def from_warn(
        cls, 
        message, 
        error, 
        status_code: int = 404
    ):
        return cls(
            message=message,
            error=error,
            status_code=status_code,
            color='warning'
        )
