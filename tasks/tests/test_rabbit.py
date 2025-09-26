import json
import pytest
import asyncio
from unittest.mock import AsyncMock, MagicMock
from fastapi import HTTPException
from api.lib.rabbit import broadcast_message
from api.deps.rabbit_conn import get_channel


@pytest.mark.asyncio
async def test_broadcast_message_publishes_with_expected_body():
    # Arrange
    exchange_name = "test_exchange"
    payload = {"hello": "world", "n": 42}

    # Mock exchange with async publish
    exchange = MagicMock()
    exchange.publish = AsyncMock(return_value=None)

    # Mock channel to return the mocked exchange on declare
    channel = MagicMock()
    channel.declare_exchange = AsyncMock(return_value=exchange)

    # Act
    await broadcast_message(channel, payload, exchange_name)

    # Assert declare_exchange called with expected name
    channel.declare_exchange.assert_awaited()
    assert channel.declare_exchange.call_args.kwargs.get("durable") is True

    # Assert publish called with Message containing serialized payload
    assert exchange.publish.await_count == 1
    msg_arg = exchange.publish.call_args.args[0]
    assert hasattr(msg_arg, "body")
    body = msg_arg.body
    decoded = json.loads(body.decode())
    assert decoded == {"data": payload}

@pytest.mark.asyncio
async def test_broadcast_message_raises_on_publish_error():
    # Arrange
    exchange = MagicMock()
    exchange.publish = AsyncMock(side_effect=RuntimeError("publish failed"))
    channel = MagicMock()
    channel.declare_exchange = AsyncMock(return_value=exchange)

    # Act / Assert
    with pytest.raises(RuntimeError):
        await broadcast_message(channel, {"x": 1}, "ex")

def test_get_channel_success():
    class State:
        pass

    class App:
        def __init__(self):
            self.state = State()

    class Req:
        def __init__(self):
            self.app = App()

    fake_channel = object()
    req = Req()
    req.app.state.rabbit_channel = fake_channel

    assert get_channel.__code__.co_flags & 0x80  # is coroutine

    # Run the coroutine to get the channel
    import asyncio

    result = asyncio.get_event_loop().run_until_complete(get_channel(req))
    assert result is fake_channel


def test_get_channel_failure_raises_http_exception():
    class Req:
        pass  # Missing app.state should trigger exception path

    with pytest.raises(HTTPException) as exc:
        asyncio.get_event_loop().run_until_complete(get_channel(Req()))

    assert exc.value.status_code == 404
    assert exc.value.detail == "RabbitMQ channel not available"