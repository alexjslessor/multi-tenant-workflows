import json
from unittest.mock import AsyncMock, MagicMock

import pytest
import aio_pika

from api_lib.lib.rabbit import (
    RabbitPublisher,
    RabbitConsumer,
    StaticChannelProvider,
    ConnectionChannelProvider,
)


pytestmark = pytest.mark.asyncio


class FakeMessage:
    def __init__(self, body: bytes = b"{}"):
        self.body = body

    def process(self):
        class _CM:
            async def __aenter__(self_inner):
                return None

            async def __aexit__(self_inner, exc_type, exc, tb):
                return False

        return _CM()


async def test_publisher_declares_exchange_and_publishes_json():
    channel = AsyncMock()
    exchange = AsyncMock()
    channel.declare_exchange.return_value = exchange

    provider = StaticChannelProvider(channel)
    publisher = RabbitPublisher(provider)

    payload = {"hello": "world"}
    await publisher.publish(
        "test-ex", payload, exchange_type=aio_pika.ExchangeType.FANOUT
    )

    channel.declare_exchange.assert_awaited_once()
    args, kwargs = channel.declare_exchange.await_args
    assert args[0] == "test-ex"

    assert exchange.publish.await_count == 1
    msg_arg, *_ = exchange.publish.await_args[0]
    assert isinstance(msg_arg, aio_pika.Message)
    # Verify body encodes JSON
    assert json.loads(msg_arg.body.decode()) == payload


async def test_consumer_declares_and_starts_consuming():
    channel = AsyncMock()
    exchange = AsyncMock()
    queue = AsyncMock()
    channel.declare_exchange.return_value = exchange
    channel.declare_queue.return_value = queue
    queue.consume.return_value = "ctag-1"

    provider = StaticChannelProvider(channel)
    consumer = RabbitConsumer(
        provider, exchange_name="ex", exchange_type=aio_pika.ExchangeType.FANOUT
    )

    cb = AsyncMock()
    tag = await consumer.start(cb)
    assert tag == "ctag-1"

    # The internal handler is passed to queue.consume; grab it and simulate a delivery
    handler = queue.consume.await_args[0][0]
    msg = FakeMessage()
    await handler(msg)
    cb.assert_awaited_once()
    (msg_passed,), _ = cb.await_args
    assert msg_passed is msg


async def test_static_channel_provider_returns_same_channel():
    channel = MagicMock()
    provider = StaticChannelProvider(channel)
    got = await provider.get_channel()
    assert got is channel