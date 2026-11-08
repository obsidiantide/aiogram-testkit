from datetime import datetime, timezone
from typing import Any, Optional

from aiogram.client.bot import Bot
from aiogram.types import CallbackQuery, Chat, InlineQuery, Message, Update, User


def create_user(
    id: int = 123456,
    is_bot: bool = False,
    first_name: str = "TestUser",
    last_name: Optional[str] = None,
    username: Optional[str] = "testuser",
    language_code: Optional[str] = "en",
    **kwargs: Any,
) -> User:
    """
    Creates a mock User with sensible defaults.
    """
    return User(
        id=id,
        is_bot=is_bot,
        first_name=first_name,
        last_name=last_name,
        username=username,
        language_code=language_code,
        **kwargs,
    )


def create_chat(
    id: int = 123456,
    type: str = "private",
    title: Optional[str] = None,
    username: Optional[str] = None,
    first_name: Optional[str] = "TestChat",
    **kwargs: Any,
) -> Chat:
    """
    Creates a mock Chat with sensible defaults.
    """
    return Chat(
        id=id,
        type=type,
        title=title,
        username=username,
        first_name=first_name,
        **kwargs,
    )


def create_message(
    text: str = "",
    chat: Optional[Chat] = None,
    from_user: Optional[User] = None,
    message_id: int = 1,
    date: Optional[datetime] = None,
    bot: Optional[Bot] = None,
    chat_id: Optional[int] = None,
    user_id: Optional[int] = None,
    **kwargs: Any,
) -> Message:
    """
    Creates a mock Message with sensible defaults.
    If bot is provided, binds the message to the bot.
    """
    if chat is None:
        effective_chat_id = chat_id if chat_id is not None else 123456
        chat = create_chat(id=effective_chat_id)
    if from_user is None:
        effective_user_id = user_id if user_id is not None else 123456
        from_user = create_user(id=effective_user_id)
    if date is None:
        date = datetime.now(timezone.utc)

    msg = Message(
        message_id=message_id,
        date=date,
        chat=chat,
        from_user=from_user,
        text=text,
        **kwargs,
    )
    if bot is not None:
        msg = msg.as_(bot)
    return msg


def create_callback_query(
    data: Optional[str] = None,
    message: Optional[Message] = None,
    from_user: Optional[User] = None,
    id: str = "cb_query_1",
    chat_instance: str = "test_instance",
    bot: Optional[Bot] = None,
    chat_id: Optional[int] = None,
    user_id: Optional[int] = None,
    **kwargs: Any,
) -> CallbackQuery:
    """
    Creates a mock CallbackQuery with sensible defaults.
    If bot is provided, binds both the query and its inner message to the bot.
    """
    if from_user is None:
        effective_user_id = user_id if user_id is not None else 123456
        from_user = create_user(id=effective_user_id)
    if message is None:
        message = create_message(bot=bot, chat_id=chat_id)
    elif bot is not None:
        message = message.as_(bot)

    cb = CallbackQuery(
        id=id,
        from_user=from_user,
        chat_instance=chat_instance,
        message=message,
        data=data,
        **kwargs,
    )
    if bot is not None:
        cb = cb.as_(bot)
    return cb


def create_inline_query(
    query: str = "",
    from_user: Optional[User] = None,
    id: str = "inline_query_1",
    offset: str = "",
    bot: Optional[Bot] = None,
    user_id: Optional[int] = None,
    **kwargs: Any,
) -> InlineQuery:
    """
    Creates a mock InlineQuery with sensible defaults.
    If bot is provided, binds the query to the bot.
    """
    if from_user is None:
        effective_user_id = user_id if user_id is not None else 123456
        from_user = create_user(id=effective_user_id)

    iq = InlineQuery(
        id=id,
        from_user=from_user,
        query=query,
        offset=offset,
        **kwargs,
    )
    if bot is not None:
        iq = iq.as_(bot)
    return iq


def create_update(
    update_id: int = 10001,
    message: Optional[Message] = None,
    callback_query: Optional[CallbackQuery] = None,
    inline_query: Optional[InlineQuery] = None,
    bot: Optional[Bot] = None,
    **kwargs: Any,
) -> Update:
    """
    Creates a mock Update with sensible defaults.
    If bot is provided, binds the update to the bot.
    """
    upd = Update(
        update_id=update_id,
        message=message,
        callback_query=callback_query,
        inline_query=inline_query,
        **kwargs,
    )
    if bot is not None:
        upd = upd.as_(bot)
    return upd
