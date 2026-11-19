"""
pytest plugin exposing ready-made fixtures.

It is registered automatically through the ``pytest11`` entry point once
``aiogram-testkit`` is installed.
"""

from typing import AsyncIterator

import pytest
import pytest_asyncio
from aiogram import Bot

from .session import MockedSession


@pytest.fixture
def mocked_session() -> MockedSession:
    """A fresh :class:`MockedSession` for every test."""
    return MockedSession()


@pytest_asyncio.fixture
async def mocked_bot(mocked_session: MockedSession) -> AsyncIterator[Bot]:
    """A :class:`aiogram.Bot` bound to ``mocked_session``."""
    bot = Bot(token="1234:test", session=mocked_session)
    try:
        yield bot
    finally:
        await bot.session.close()
