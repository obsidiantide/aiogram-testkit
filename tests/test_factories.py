from datetime import datetime, timezone

import pytest
from aiogram import Bot
from aiogram.methods import AnswerCallbackQuery, EditMessageText, SendMessage
from aiogram.types import CallbackQuery, Chat, Message, Update, User
from aiogram_testkit import (
    MockedSession,
    create_callback_query,
    create_chat,
    create_inline_query,
    create_message,
    create_update,
    create_user,
)


def test_create_user_defaults():
    user = create_user()
    assert isinstance(user, User)
    assert user.id == 123456
    assert user.is_bot is False
    assert user.first_name == "TestUser"
    assert user.username == "testuser"
    assert user.language_code == "en"


def test_create_user_custom():
    user = create_user(
        id=42,
        is_bot=True,
        first_name="CustomBot",
        last_name="Agent",
        username="custom_bot",
        language_code="az",
    )
    assert user.id == 42
    assert user.is_bot is True
    assert user.first_name == "CustomBot"
    assert user.last_name == "Agent"
    assert user.username == "custom_bot"
    assert user.language_code == "az"


def test_create_chat_defaults():
    chat = create_chat()
    assert isinstance(chat, Chat)
    assert chat.id == 123456
    assert chat.type == "private"
    assert chat.first_name == "TestChat"


def test_create_chat_custom():
    chat = create_chat(id=-1001234567, type="supergroup", title="Developers Chat")
    assert chat.id == -1001234567
    assert chat.type == "supergroup"
    assert chat.title == "Developers Chat"


def test_create_message_defaults():
    msg = create_message(text="hello")
    assert isinstance(msg, Message)
    assert msg.text == "hello"
    assert msg.message_id == 1
    assert msg.chat.id == 123456
    assert msg.from_user.id == 123456
    assert isinstance(msg.date, datetime)


def test_create_message_with_custom_ids():
    custom_date = datetime(2026, 1, 1, 12, 0, 0, tzinfo=timezone.utc)
    msg = create_message(
        text="/help",
        chat_id=999,
        user_id=777,
        message_id=42,
        date=custom_date,
    )
    assert msg.text == "/help"
    assert msg.message_id == 42
    assert msg.chat.id == 999
    assert msg.from_user.id == 777
    assert msg.date == custom_date


@pytest.mark.asyncio
async def test_create_message_bound_to_bot():
    session = MockedSession()
    bot = Bot(token="1234:test", session=session)

    session.add_result(
        "SendMessage",
        create_message(text="response", chat_id=10),
    )

    msg = create_message(text="/start", chat_id=10, bot=bot)
    assert msg.bot is bot

    sent = await msg.answer("response")
    assert sent.text == "response"
    assert session.count_requests() == 1
    assert session.count_requests(SendMessage) == 1
    assert session.has_request(SendMessage)


def test_create_callback_query_defaults():
    cb = create_callback_query(data="press_button")
    assert isinstance(cb, CallbackQuery)
    assert cb.data == "press_button"
    assert cb.id == "cb_query_1"
    assert cb.from_user.id == 123456
    assert isinstance(cb.message, Message)


@pytest.mark.asyncio
async def test_create_callback_query_bound_to_bot():
    session = MockedSession()
    bot = Bot(token="1234:test", session=session)

    session.add_result("AnswerCallbackQuery", True)
    session.add_result(
        "EditMessageText",
        create_message(text="updated", chat_id=50),
    )

    cb = create_callback_query(data="confirm", chat_id=50, bot=bot)
    assert cb.bot is bot
    assert cb.message.bot is bot

    res = await cb.answer("Confirmed")
    assert res is True
    assert session.has_request(AnswerCallbackQuery)

    edited = await cb.message.edit_text("updated")
    assert edited.text == "updated"
    assert session.has_request(EditMessageText)
    assert session.count_requests() == 2
    assert session.count_requests(AnswerCallbackQuery) == 1
    assert session.count_requests(EditMessageText) == 1


def test_create_update():
    msg = create_message(text="hello")
    upd = create_update(update_id=555, message=msg)
    assert isinstance(upd, Update)
    assert upd.update_id == 555
    assert upd.message.text == "hello"
    assert upd.callback_query is None


def test_create_update_with_callback_query():
    cb = create_callback_query(data="menu_nav")
    upd = create_update(update_id=777, callback_query=cb)
    assert upd.update_id == 777
    assert upd.callback_query.data == "menu_nav"
    assert upd.message is None


def test_mocked_session_count_requests():
    session = MockedSession()
    assert session.count_requests() == 0
    assert session.count_requests(SendMessage) == 0


def test_create_inline_query_defaults():
    iq = create_inline_query()
    assert iq.query == ""
    assert iq.offset == ""
    assert iq.from_user.id == 123456


def test_create_inline_query_custom_values():
    iq = create_inline_query(query="cats", offset="10", user_id=42, id="q7")
    assert (iq.id, iq.query, iq.offset, iq.from_user.id) == ("q7", "cats", "10", 42)


@pytest.mark.asyncio
async def test_create_inline_query_bound_to_bot_can_answer():
    session = MockedSession()
    bot = Bot(token="1234:test", session=session)
    iq = create_inline_query(query="x", bot=bot)
    await iq.answer(results=[])
    assert session.count_requests() == 1


def test_create_update_with_inline_query():
    upd = create_update(inline_query=create_inline_query(query="hi"))
    assert upd.inline_query.query == "hi"
    assert upd.message is None
