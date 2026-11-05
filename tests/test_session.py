import pytest
from aiogram import Bot
from aiogram.methods import SendMessage, DeleteMessage
from aiogram.types import Message, Chat
from aiogram_testkit import MockedSession


@pytest.mark.asyncio
async def test_mocked_session_send_message():
    session = MockedSession()
    bot = Bot(token="1234:test", session=session)

    mocked_message = Message(
        message_id=1,
        date=1234567890,
        chat=Chat(id=123, type="private"),
        text="Hello world",
    )
    session.add_result("SendMessage", mocked_message)

    result = await bot.send_message(chat_id=123, text="Hello world")

    assert result.message_id == 1
    assert result.text == "Hello world"

    assert len(session.requests) == 1
    assert isinstance(session.requests[0], SendMessage)
    assert session.requests[0].text == "Hello world"
    assert session.requests[0].chat_id == 123


@pytest.mark.asyncio
async def test_mocked_session_helpers():
    session = MockedSession()
    bot = Bot(token="1234:test", session=session)

    session.add_result("SendMessage", Message(
        message_id=10,
        date=1234567890,
        chat=Chat(id=42, type="private"),
        text="First",
    ))
    session.add_result("DeleteMessage", True)

    assert session.last_request is None
    assert not session.has_request(SendMessage)

    await bot.send_message(chat_id=42, text="First")
    await bot.delete_message(chat_id=42, message_id=10)

    assert len(session.requests) == 2
    assert session.has_request(SendMessage)
    assert session.has_request(DeleteMessage)

    first_send = session.get_request(SendMessage)
    assert first_send is not None
    assert first_send.text == "First"

    del_req = session.get_request(DeleteMessage)
    assert del_req is not None
    assert del_req.message_id == 10

    assert isinstance(session.last_request, DeleteMessage)

    all_sends = session.find_requests(SendMessage)
    assert len(all_sends) == 1


@pytest.mark.asyncio
async def test_mocked_session_reset():
    session = MockedSession()
    bot = Bot(token="1234:test", session=session)

    session.add_result("SendMessage", Message(
        message_id=1,
        date=1234567890,
        chat=Chat(id=1, type="private"),
        text="Test",
    ))

    await bot.send_message(chat_id=1, text="Test")
    assert len(session.requests) == 1
    assert "SendMessage" in session.responses

    session.reset()
    assert len(session.requests) == 0
    assert len(session.responses) == 0
    assert session.last_request is None


@pytest.mark.asyncio
async def test_mocked_session_stream_content_and_close():
    session = MockedSession()
    await session.close()

    chunks = []
    async for chunk in session.stream_content("https://example.com/file"):
        chunks.append(chunk)

    assert chunks == [b""]


@pytest.mark.asyncio
async def test_mocked_session_raises_mocked_exception():
    session = MockedSession()
    bot = Bot(token="1234:test", session=session)
    session.add_result("SendMessage", RuntimeError("blocked by user"))

    with pytest.raises(RuntimeError, match="blocked by user"):
        await bot.send_message(chat_id=1, text="hi")

    # The failed request is still recorded for inspection.
    assert session.count_requests(SendMessage) == 1


@pytest.mark.asyncio
async def test_mocked_session_callable_result_receives_request():
    session = MockedSession()
    bot = Bot(token="1234:test", session=session)
    session.add_result(
        "SendMessage",
        lambda method: Message(
            message_id=7,
            date=1234567890,
            chat=Chat(id=method.chat_id, type="private"),
            text=method.text.upper(),
        ),
    )

    result = await bot.send_message(chat_id=55, text="echo")

    assert result.chat.id == 55
    assert result.text == "ECHO"
