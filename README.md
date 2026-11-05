# aiogram-testkit

A lightweight toolkit for testing [aiogram](https://github.com/aiogram/aiogram) (v3.x) bots in `pytest` without making real Telegram Bot API network requests.

## Features

- **MockedSession**: In-memory `BaseSession` implementation that records all outgoing bot requests and returns predefined responses.
- **Dynamic Responses**: `add_result` accepts a value, an exception to raise (e.g. simulate `TelegramForbiddenError`), or a callable that builds the response from the request.
- **Request Inspection**: Query recorded requests with helpers like `get_request`, `find_requests`, `has_request`, `count_requests`, and `last_request`.
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
