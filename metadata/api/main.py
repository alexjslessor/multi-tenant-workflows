import logging
import logging.config
from fastapi import (
    FastAPI,
    HTTPException,
    Request,
    FastAPI,
)
from fastapi.encoders import jsonable_encoder
from fastapi.exceptions import RequestValidationError, ResponseValidationError
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from typing import Any
from pydantic import (
    BaseModel, 
    Field, 
    ValidationError
)
from .logs import LOGGING_CONFIG
from .settings import get_settings
from .on_startup import lifespan

logging.config.dictConfig(LOGGING_CONFIG)
logger = logging.getLogger("uvicorn")
logger_err = logging.getLogger("uvicorn.error")
settings = get_settings()
SECRET = settings.SECRET
DATABASE_URL = settings.postgres_url
DBNAME = settings.DBNAME
LIFETIME_SECONDS = settings.LIFETIME_SECONDS

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
        self.error = error
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
    '''
    {'loc': ('response', 0, 'consumption_usage'), 'msg': "consumption_usage is not a valid:  - could not convert string to float: ''", 'type': 'value_error'}
    '''
    try:
        return ' '.join([f"{i['loc'][2]}: {i['msg']}" for i in excp.errors()])
    except (IndexError, AttributeError) as e:
        msg = (
                'ResponseValidationError: '
                'could not parse e.errors() to create response message: '
        )
        logger.debug(msg)
        raise Exception(msg)

app = FastAPI(
    title=settings.TITLE,
    openapi_url=settings.OPENAPI_URL,
    docs_url=settings.DOCS_URL,
    redoc_url=None,
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=settings.CORS_ALLOW_CREDS,
    allow_methods=settings.CORS_ALLOW_METHODS,
    allow_headers=settings.CORS_ALLOW_HEADERS,
)

@app.exception_handler(PostException)
def post_exc_handler(req: Request, ex: PostException):
    e = JSONResponse(
        status_code=ex.status_code, 
        content={"error": f"{ex!s}"})
    return e

@app.exception_handler(FrontendException)
def frontend_exception_handler(req: Request, ex: FrontendException):
    return JSONResponse(
        status_code=ex.status_code,
        content={
            "message": f"{ex.message}",
            'error': f'{ex.error}',
            "color": f"{ex.color}"
        }
    )

@app.exception_handler(RequestValidationError)
async def request_body_validation_error(request: Request, exc: RequestValidationError):
    try:
        logger.info(exc)
        err_msg = parse_request_validation_error(exc)
        msg = ErrorSchema(message=str(err_msg), error=str(exc.body), color='error').model_dump()
        logger.info(msg['message'])
        return JSONResponse(status_code=422, content=msg)
    except Exception as e:
        msg = ErrorSchema(
            message=f'Could not create request validation error. Contact your Sys Admin: {e!r}', 
            error=str(exc.body), 
            color='error'
        ).model_dump()
        logger.info(f'{msg!r}')
        return JSONResponse(status_code=500, content=jsonable_encoder(msg))

@app.exception_handler(ResponseValidationError)
async def response_validation_exc_handler(
    request: Request, 
    ex: ResponseValidationError,
):
    try:
        content={
            "message": f"Internal Server Error",
            'data': f"Response Validation Error: {request.url.path}",
            "color": f"red",
            'status_code': 500,
        }
        return content
    except Exception as e:
        return JSONResponse(
            status_code=500,
            content={"message": "Internal Server Error"},
        )

@app.middleware("http")
async def middleware_log(request: Request, call_next):
    try:
        response = await call_next(request)
        return response
    except Exception as e:
        obj = {
            'error': f'Unknown middleware error: {e!s}', 
            'message': 'Unknown error, please contact your system admin', 
            'color': 'error'
        }
        return JSONResponse(status_code=500, content=jsonable_encoder(obj))