"""Examples from the README: FSM flows and middleware tested through feed_update."""

from typing import Any, Awaitable, Callable, Dict

import pytest
from aiogram import BaseMiddleware, Bot, Dispatcher, F
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.types import Message, TelegramObject

from aiogram_testkit import create_message, create_update, feed_update


class Form(StatesGroup):
    name = State()


class CounterMiddleware(BaseMiddleware):
    def __init__(self) -> None:
        self.seen = 0

    async def __call__(
        self,
        handler: Callable[[TelegramObject, Dict[str, Any]], Awaitable[Any]],
        event: TelegramObject,
        data: Dict[str, Any],
    ) -> Any:
        self.seen += 1
        data["seen"] = self.seen
        return await handler(event, data)


def _fsm_dispatcher() -> Dispatcher:
    dp = Dispatcher()

    @dp.message(Command("register"))
    async def register(message: Message, state: FSMContext) -> None:
        await state.set_state(Form.name)
        await message.answer("What is your name?")

    @dp.message(Form.name)
    async def got_name(message: Message, state: FSMContext) -> None:
        await state.update_data(name=message.text)
        await state.clear()
        await message.answer(f"Nice to meet you, {message.text}!")

    return dp


def _message_update(bot: Bot, text: str, update_id: int) -> Any:
    return create_update(update_id=update_id, message=create_message(text=text, bot=bot))


@pytest.mark.asyncio
async def test_fsm_conversation_spans_several_updates(mocked_bot: Bot) -> None:
    dp = _fsm_dispatcher()

    first = await feed_update(dp, mocked_bot, _message_update(mocked_bot, "/register", 1))
    second = await feed_update(dp, mocked_bot, _message_update(mocked_bot, "Alice", 2))

    assert first[0].text == "What is your name?"
    assert second[0].text == "Nice to meet you, Alice!"


@pytest.mark.asyncio
async def test_fsm_text_without_state_is_not_handled(mocked_bot: Bot) -> None:
    dp = _fsm_dispatcher()

    requests = await feed_update(dp, mocked_bot, _message_update(mocked_bot, "Alice", 1))

    assert requests == []


@pytest.mark.asyncio
async def test_middleware_injects_data_into_handlers(mocked_bot: Bot) -> None:
    dp = Dispatcher()
    counter = CounterMiddleware()
    dp.message.middleware(counter)

    @dp.message(F.text == "/count")
    async def count(message: Message, seen: int) -> None:
        await message.answer(f"seen={seen}")

    first = await feed_update(dp, mocked_bot, _message_update(mocked_bot, "/count", 1))
    second = await feed_update(dp, mocked_bot, _message_update(mocked_bot, "/count", 2))

    assert first[0].text == "seen=1"
    assert second[0].text == "seen=2"
    assert counter.seen == 2


@pytest.mark.asyncio
async def test_feed_update_forwards_workflow_data(mocked_bot: Bot) -> None:
    dp = Dispatcher()

    @dp.message(F.text == "/who")
    async def who(message: Message, role: str) -> None:
        await message.answer(role)

    requests = await feed_update(
        dp, mocked_bot, _message_update(mocked_bot, "/who", 1), role="admin"
    )

    assert requests[0].text == "admin"
