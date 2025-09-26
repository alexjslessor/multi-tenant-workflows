import logging
import aio_pika
from typing import Any
from pydantic import BaseModel
from api_lib.lib.rabbit import RabbitPublisher, StaticChannelProvider

logger = logging.getLogger('uvicorn')

class RabbitMessage(BaseModel):
    data: dict

async def broadcast_message(
    channel: aio_pika.Channel, 
    message: dict[str, Any],
    exchange: str,
):
    """Broadcast a message on the "video-uploaded" exchange.
    Is received by the metadata service.

    Args:
        channel (aio_pika.Channel): _description_
        video_metadata (MetadataItem): _description_

    Returns:
        _type_: _description_
    """
    try:
        provider = StaticChannelProvider(channel)
        publisher = RabbitPublisher(provider)
        body = RabbitMessage(data=message).model_dump()
        await publisher.publish(exchange, body, exchange_type=aio_pika.ExchangeType.FANOUT)
    except Exception as e:
        logger.error(f"Error broadcasting message: {e}")
        raise
