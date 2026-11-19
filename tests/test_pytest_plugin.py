import pytest
from aiogram import Bot
from aiogram.methods import SendMessage

from aiogram_testkit import MockedSession, create_chat


def test_mocked_session_fixture_is_a_fresh_session(mocked_session):
    assert isinstance(mocked_session, MockedSession)
    assert mocked_session.requests == []


@pytest.mark.asyncio
async def test_mocked_bot_uses_mocked_session(mocked_bot, mocked_session):
    assert isinstance(mocked_bot, Bot)
    assert mocked_bot.session is mocked_session

    mocked_session.add_result("SendMessage", {"message_id": 1, "date": 0, "chat": create_chat().model_dump()})
    await mocked_bot.send_message(chat_id=1, text="hi")

    assert len(mocked_session.requests) == 1
    request = mocked_session.requests[0]
    assert isinstance(request, SendMessage)
    assert request.text == "hi"


def test_mocked_session_is_not_shared_between_tests(mocked_session):
    assert mocked_session.responses == {}
