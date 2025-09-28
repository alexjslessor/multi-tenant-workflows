import redis
import aio_pika
import datetime
import logging
import logging.config
from contextlib import asynccontextmanager
from sqlalchemy.ext.asyncio import (
    async_sessionmaker, 
    create_async_engine, 
)
from fastapi.middleware.cors import CORSMiddleware
from fastapi.exceptions import RequestValidationError, ResponseValidationError
from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse

from api_lib.lib import (
    LOGGING_CONFIG,
    connect_to_rabbitmq,
    FrontendException,
)
from .lib.error_schema import responses
from .settings import get_settings
from .db import create_all_tables
from .routes import (
    job_routes, 
    workflow_routes,
    workflow_result_routes,
)

settings = get_settings()
logger = logging.getLogger("tasks")

@asynccontextmanager
async def lifespan(app: FastAPI):
    try:
        logging.config.dictConfig(LOGGING_CONFIG)
        engine_async = create_async_engine(settings.POSTGRES_URL_ASYNC)
        await create_all_tables(engine_async)
        async_session_maker = async_sessionmaker(
            engine_async, 
            expire_on_commit=False,
        )

        rabbit_con = await connect_to_rabbitmq(settings.RABBIT)
        rabbit_channel = await rabbit_con.channel()
        # await rabbit_channel.declare_exchange(
        #     "create_workflow", 
        #     aio_pika.ExchangeType.FANOUT, 
        #     durable=True
        # )
        app.state.rabbit_con = rabbit_con
        app.state.rabbit_channel = rabbit_channel
        app.state.redis_client = redis.from_url(settings.REDIS_URL)
        app.state.async_session_maker = async_session_maker
        yield
        # Taredown
        app.state.redis_client.close()
        await app.state.rabbit_channel.close()
        await app.state.rabbit_con.close()
    except Exception as e:
        logger.error(e)
        raise

app = FastAPI(
    title=settings.TITLE,
    openapi_url=settings.OPENAPI_URL,
    docs_url=settings.DOCS_URL,
    redoc_url=None,
    lifespan=lifespan,
)

@app.exception_handler(FrontendException)
def frontend_exception_handler(
    req: Request, 
    ex: FrontendException,
):
    return JSONResponse(
        status_code=ex.status_code,
        content={
            "message": f"{ex.detail}",
            'error': f'{ex.error}',
            "color": f"{ex.color}"
        }
    )

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
    start_time = datetime.datetime.now()
    response = await call_next(request)
    process_time = datetime.datetime.now() - start_time
    response.headers["X-Time-Elapsed"] = str(process_time)
    return response

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_methods=settings.CORS_ALLOW_METHODS,
    allow_headers=settings.CORS_ALLOW_HEADERS,
    allow_credentials=settings.CORS_ALLOW_CREDENTIALS,
)

app.include_router(
    job_routes.router, prefix=settings.PREFIX, tags=['jobs'], responses=responses)
app.include_router(
    workflow_routes.router, prefix=settings.PREFIX, tags=['workflows'], responses=responses)
app.include_router(
    workflow_result_routes.router, prefix=settings.PREFIX, tags=['workflow_results'], responses=responses)