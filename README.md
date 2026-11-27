# aiogram-testkit

A lightweight toolkit for testing [aiogram](https://github.com/aiogram/aiogram) (v3.x) bots in `pytest` without making real Telegram Bot API network requests.

## Features

- **MockedSession**: In-memory `BaseSession` implementation that records all outgoing bot requests and returns predefined responses.
- **Dynamic Responses**: `add_result` accepts a value, an exception to raise (e.g. simulate `TelegramForbiddenError`), or a callable that builds the response from the request.
- **Per-call Results**: `add_results("SendMessage", first, second, ...)` returns (or raises) a different result on each successive call; the last one repeats.
- **Request Inspection**: Query recorded requests with helpers like `get_request`, `find_requests`, `has_request`, `count_requests`, and `last_request`.
- **Dispatcher Helper**: `feed_update(dp, bot, update)` runs an update through your handlers and returns the requests they made.
- **Event Factories**: Helpers (`create_message`, `create_user`, `create_chat`, `create_callback_query`, `create_update`) with sensible defaults for quick testing.
- **Zero External Mocks**: Clean, type-safe API that does not require monkeypatching `aiohttp`.

## Installation

```bash
pip install aiogram-testkit
```

## Quick Start

```python
import pytest
from aiogram import Bot
from aiogram.methods import SendMessage
from aiogram_testkit import MockedSession, create_message

@pytest.mark.asyncio
async def test_bot_send_message():
    session = MockedSession()
    bot = Bot(token="1234:TEST", session=session)

    # Mock response with factory helper
    session.add_result(
        "SendMessage",
        create_message(text="pong", chat_id=42),
    )

    # Trigger bot logic
    result = await bot.send_message(chat_id=42, text="ping")

    assert result.text == "pong"
    assert session.has_request(SendMessage)
    assert session.last_request.chat_id == 42
```

## Testing handlers through a Dispatcher

`feed_update` pushes an update through a `Dispatcher` and returns only the requests the bot made while handling it:

```python
from aiogram import Bot, Dispatcher, F
from aiogram.types import Message
from aiogram_testkit import MockedSession, create_message, create_update, feed_update

dp = Dispatcher()

@dp.message(F.text == "/start")
async def start(message: Message) -> None:
    await message.answer("Welcome!")

async def test_start():
    bot = Bot(token="1234:TEST", session=MockedSession())
    update = create_update(message=create_message(text="/start", bot=bot))

    requests = await feed_update(dp, bot, update)

    assert requests[0].text == "Welcome!"
```

Extra keyword arguments are passed to `Dispatcher.feed_update` as workflow data.

## FSM and middleware

State lives in the dispatcher's storage (`MemoryStorage` by default), so a multi-step conversation is just several `feed_update` calls against the same `Dispatcher`:

```python
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup

class Form(StatesGroup):
    name = State()

dp = Dispatcher()

@dp.message(Command("register"))
async def register(message: Message, state: FSMContext) -> None:
    await state.set_state(Form.name)
    await message.answer("What is your name?")

@dp.message(Form.name)
async def got_name(message: Message, state: FSMContext) -> None:
    await state.clear()
    await message.answer(f"Nice to meet you, {message.text}!")

async def test_registration(mocked_bot):
    first = await feed_update(dp, mocked_bot, create_update(update_id=1, message=create_message(text="/register", bot=mocked_bot)))
    second = await feed_update(dp, mocked_bot, create_update(update_id=2, message=create_message(text="Alice", bot=mocked_bot)))

    assert first[0].text == "What is your name?"
    assert second[0].text == "Nice to meet you, Alice!"
```

Middlewares registered on the dispatcher run as usual, and anything they put into `data` is available to handlers. Keyword arguments of `feed_update` become workflow data (`feed_update(dp, bot, update, role="admin")` injects `role`). Use a distinct `update_id` for every update of a conversation.

See `tests/test_fsm_and_middleware.py` for runnable versions of these examples.

## pytest fixtures

Installing the package registers a pytest plugin with two fixtures:

- `mocked_session` — a fresh `MockedSession` for each test;
- `mocked_bot` — an `aiogram.Bot` bound to that session (closed after the test).

```python
import pytest
from aiogram_testkit import create_message, create_update, feed_update


@pytest.mark.asyncio
async def test_start(mocked_bot, mocked_session):
    mocked_session.add_result("SendMessage", ...)
    requests = await feed_update(dp, mocked_bot, create_update(message=create_message(text="/start", bot=mocked_bot)))
    assert requests[0].text == "Welcome!"
```
