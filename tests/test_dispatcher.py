import pytest
from aiogram import Bot, Dispatcher, F
from aiogram.methods import SendMessage
from aiogram.types import Message

from aiogram_testkit import MockedSession, create_message, create_update, feed_update


def _make_dispatcher() -> Dispatcher:
    dp = Dispatcher()

    @dp.message(F.text == "/start")
    async def start(message: Message) -> None:
        await message.answer("Welcome!")

    return dp


@pytest.mark.asyncio
async def test_feed_update_returns_requests_made_by_handler():
    session = MockedSession()
    bot = Bot(token="1234:test", session=session)
    dp = _make_dispatcher()

    update = create_update(message=create_message(text="/start", bot=bot))
    requests = await feed_update(dp, bot, update)

    assert len(requests) == 1
    assert isinstance(requests[0], SendMessage)
    assert requests[0].text == "Welcome!"


@pytest.mark.asyncio
async def test_feed_update_excludes_earlier_requests():
    session = MockedSession()
    bot = Bot(token="1234:test", session=session)
    dp = _make_dispatcher()

    await feed_update(dp, bot, create_update(message=create_message(text="/start", bot=bot)))
    second = await feed_update(
        dp, bot, create_update(update_id=2, message=create_message(text="/start", bot=bot))
    )

    assert len(second) == 1
    assert session.count_requests() == 2


@pytest.mark.asyncio
async def test_feed_update_unhandled_update_returns_empty_list():
    session = MockedSession()
    bot = Bot(token="1234:test", session=session)
    dp = _make_dispatcher()

    update = create_update(message=create_message(text="unknown", bot=bot))
    assert await feed_update(dp, bot, update) == []


@pytest.mark.asyncio
async def test_feed_update_forwards_workflow_data():
    session = MockedSession()
    bot = Bot(token="1234:test", session=session)
    dp = Dispatcher()

    @dp.message()
    async def handler(message: Message, greeting: str) -> None:
        await message.answer(greeting)

    update = create_update(message=create_message(text="hi", bot=bot))
    requests = await feed_update(dp, bot, update, greeting="hello")

    assert requests[0].text == "hello"


@pytest.mark.asyncio
async def test_feed_update_requires_mocked_session():
    bot = Bot(token="1234:test")
    with pytest.raises(TypeError):
        await feed_update(Dispatcher(), bot, create_update())
    await bot.session.close()
