import os
import socket
import asyncio
import logging
import logging.config
import uuid
from fastapi import FastAPI
from contextlib import asynccontextmanager
from sqlalchemy.exc import OperationalError, DBAPIError
from sqlalchemy.ext.asyncio import create_async_engine, AsyncEngine
from api.logs import LOGGING_CONFIG
from api.settings import get_settings
# from api.routers.postgres_routes import Base, engine
import aio_pika
import json

settings = get_settings()
logger = logging.getLogger('uvicorn')
logger_err = logging.getLogger("uvicorn.error")
# MAX_RETRIES = int(os.getenv("DB_STARTUP_RETRIES", "5"))
# BASE_DELAY = float(os.getenv("DB_STARTUP_DELAY", "1.5"))
engine: AsyncEngine = create_async_engine(
    settings.POSTGRES_URL_ASYNC, 
    pool_pre_ping=True,
)

async def connect_to_rabbitmq(url: str, retry: int = 5):
    for attempt in range(retry):
        try:
            return await aio_pika.connect_robust(url)
        except aio_pika.exceptions.AMQPConnectionError as e:
            if attempt < retry - 1:
                await asyncio.sleep(5)  # Retry after 5 seconds
            else:
                raise Exception("Connection to RabbitMQ failed")

async def consume_tenant_created(
    message: aio_pika.IncomingMessage, 
    # db,
):
    async with message.process():
        try:
            msg = json.loads(message.body.decode())
            logger.info(msg)
            # await db[settings.VIDEO_COLLECTION].insert_one(video_metadata)
        except Exception as e:
            logger.error(e)

async def consume_create_workflow(
    message: aio_pika.IncomingMessage, 
    # db,
):
    async with message.process():
        try:
            msg = json.loads(message.body.decode())
            logger.info(msg)
            # metadata = {
            #     "id": msg["id"],
            #     "slug": msg["slug"],
            #     "tenant_id": msg["tenant_id"],
            # }
            # await db[settings.VIDEO_COLLECTION].insert_one(video_metadata)
        except Exception as e:
            logger.error(e)

@asynccontextmanager
async def lifespan(app: FastAPI):
    logging.config.dictConfig(LOGGING_CONFIG)

    rabbit_connection = await connect_to_rabbitmq(settings.RABBIT)
    rabbit_channel = await rabbit_connection.channel()
    try:
        # 1
        ex_1 = await rabbit_channel.declare_exchange(
            "create_workflow", 
            aio_pika.ExchangeType.FANOUT, 
            durable=True
        )
        queue_1 = await rabbit_channel.declare_queue("", exclusive=True)
        await queue_1.bind(ex_1)
        await queue_1.consume(
            lambda message: consume_create_workflow(message)
        )



        yield
    finally:
        await engine.dispose()
        logger.info("Engine Disposed.")