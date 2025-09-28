import json
import logging
import logging.config
from fastapi import FastAPI
from contextlib import asynccontextmanager
# from sqlalchemy.exc import OperationalError, DBAPIError
from sqlalchemy.ext.asyncio import create_async_engine, AsyncEngine
from api_lib.lib import (
    LOGGING_CONFIG,
    connect_to_rabbitmq,
)
from api.settings import get_settings
import aio_pika
from aio_pika.abc import AbstractRobustConnection as RabbitConType

settings = get_settings()
logger = logging.getLogger('metadata')
logger_err = logging.getLogger("uvicorn.error")

engine: AsyncEngine = create_async_engine(
    settings.POSTGRES_URL_ASYNC, 
    pool_pre_ping=True,
)

async def consume_create_workflow(
    message: aio_pika.abc.AbstractIncomingMessage, 
):
    async with message.process():
        try:
            msg = json.loads(message.body.decode())
            logger.info(msg)
        except Exception as e:
            logger.error(f"Error processing message: {e}")

@asynccontextmanager
async def lifespan(app: FastAPI):
    try:
        logging.config.dictConfig(LOGGING_CONFIG)

        rabbit_con: RabbitConType = await connect_to_rabbitmq(settings.RABBIT)
        rabbit_channel = await rabbit_con.channel()
        # exchange-1
        ex_1 = await rabbit_channel.declare_exchange(
            name="create_workflow", 
            type=aio_pika.ExchangeType.FANOUT, 
            durable=True,
        )
        queue_1 = await rabbit_channel.declare_queue(
            "metadata-que", 
            exclusive=True,
        )
        await queue_1.bind(
            exchange=ex_1,
        )
        await queue_1.consume(
            lambda message: consume_create_workflow(message),
        )
        yield
    except Exception as e:
        logger.error(e)
        raise
    finally:
        await engine.dispose()
        logger.info("Engine Disposed.")