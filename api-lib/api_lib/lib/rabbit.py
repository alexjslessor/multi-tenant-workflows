import asyncio
from typing import Any, Awaitable, Callable, Optional, Protocol
import aio_pika


async def connect_to_rabbitmq(
    url: str, 
    retry: int = 5,
) -> aio_pika.abc.AbstractRobustConnection:
    for attempt in range(retry):
        try:
            return await aio_pika.connect_robust(url)
        except aio_pika.exceptions.AMQPConnectionError:
            if attempt < retry - 1:
                await asyncio.sleep(5)
            else:
                raise Exception("Connection to RabbitMQ failed")
    raise Exception("Connection to RabbitMQ failed")

class ChannelProvider(Protocol):
    async def get_channel(self) -> aio_pika.abc.AbstractChannel:
        ...

class ConnectionChannelProvider:
    """Channel provider backed by a robust connection.

    Lazily creates a channel on first use and reuses it.
    """

    def __init__(self, connection: aio_pika.abc.AbstractRobustConnection):
        self._connection = connection
        self._channel: Optional[aio_pika.abc.AbstractChannel] = None

    async def get_channel(self) -> aio_pika.abc.AbstractChannel:
        if self._channel is None or self._channel.is_closed:
            self._channel = await self._connection.channel()
        return self._channel

class StaticChannelProvider:
    """Channel provider that returns a pre-created channel (for DI/adapters)."""

    def __init__(self, channel: aio_pika.abc.AbstractChannel):
        self._channel = channel

    async def get_channel(self) -> aio_pika.abc.AbstractChannel:
        return self._channel

class RabbitPublisher:
    """Simple publisher with exchange auto-declare.

    Usage:
        conn = await connect_to_rabbitmq(url)
        publisher = RabbitPublisher(ConnectionChannelProvider(conn))
        await publisher.publish("exchange", {"hello": "world"})
    """

    def __init__(self, channel_provider: ChannelProvider):
        self._provider = channel_provider

    async def publish(
        self,
        exchange_name: str,
        message: Any,
        *,
        exchange_type: aio_pika.ExchangeType = aio_pika.ExchangeType.FANOUT,
        routing_key: str = "",
        durable: bool = True,
        content_type: str = "application/json",
    ) -> None:
        channel = await self._provider.get_channel()
        exchange = await channel.declare_exchange(
            exchange_name, exchange_type, durable=durable
        )

        if isinstance(message, (bytes, bytearray)):
            body = bytes(message)
            content_type_hdr = content_type
        elif isinstance(message, str):
            body = message.encode()
            content_type_hdr = "text/plain"
        else:
            # Fallback to JSON via pydantic-free approach
            import json

            body = json.dumps(message, default=str).encode()
            content_type_hdr = content_type

        msg = aio_pika.Message(body=body, content_type=content_type_hdr)
        await exchange.publish(msg, routing_key=routing_key)


class RabbitConsumer:
    """Declarative consumer that binds a queue to an exchange and consumes.

    The class accepts a channel provider dependency, then on start will:
    - create a channel
    - declare the exchange
    - declare a queue and bind it to the exchange
    - start consuming with the given callback
    """

    def __init__(
        self,
        channel_provider: ChannelProvider,
        *,
        exchange_name: str,
        queue_name: Optional[str] = None,
        exchange_type: aio_pika.ExchangeType = aio_pika.ExchangeType.FANOUT,
        routing_key: str = "",
        durable: bool = True,
        exclusive: Optional[bool] = None,
        auto_delete: Optional[bool] = None,
        prefetch_count: Optional[int] = None,
    ):
        self._provider = channel_provider
        self.exchange_name = exchange_name
        self.queue_name = queue_name
        self.exchange_type = exchange_type
        self.routing_key = routing_key
        self.durable = durable
        self.exclusive = exclusive
        self.auto_delete = auto_delete
        self.prefetch_count = prefetch_count

    async def start(
        self, 
        callback: Callable[[aio_pika.abc.AbstractIncomingMessage], Awaitable[None]]
    ) -> str:
        channel = await self._provider.get_channel()
        if self.prefetch_count:
            await channel.set_qos(prefetch_count=self.prefetch_count)

        exchange = await channel.declare_exchange(
            self.exchange_name, self.exchange_type, durable=self.durable
        )

        # If no queue name is provided, create an exclusive, autodelete queue
        exclusive = True if self.queue_name is None else (self.exclusive or False)
        auto_delete = True if self.queue_name is None else (self.auto_delete or False)

        queue = await channel.declare_queue(
            name=self.queue_name or "",
            durable=self.durable if not exclusive else False,
            exclusive=exclusive,
            auto_delete=auto_delete,
        )

        await queue.bind(exchange, routing_key=self.routing_key)

        async def _handler(message: aio_pika.abc.AbstractIncomingMessage) -> None:
            # Ensure message is acked/nacked appropriately via context manager
            async with message.process():
                await callback(message)

        consumer_tag = await queue.consume(_handler)
        return consumer_tag