from typing import Any, List

from aiogram import Bot, Dispatcher
from aiogram.methods import TelegramMethod
from aiogram.types import Update

from .session import MockedSession


async def feed_update(
    dispatcher: Dispatcher,
    bot: Bot,
    update: Update,
    **kwargs: Any,
) -> List[TelegramMethod[Any]]:
    """
    Feed ``update`` to ``dispatcher`` and return the requests the bot made
    while handling it.

    ``bot`` must use a :class:`MockedSession`; requests recorded before the
    call are not included. Extra keyword arguments are forwarded to
    :meth:`aiogram.Dispatcher.feed_update` (e.g. workflow data).
    """
    session = bot.session
    if not isinstance(session, MockedSession):
        raise TypeError("bot must be created with a MockedSession")

    start = len(session.requests)
    await dispatcher.feed_update(bot, update, **kwargs)
    return list(session.requests[start:])
