import functools
import inspect
from typing import Any, Callable, Optional

from aiogram import types

from utils import service


class Message(types.Message):
    """Customized Message class"""

    def __init__(self, bot: service.Bot, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.as_(bot)

    """Customized Message class"""

    async def safe_edit(
        self: types.Message,
        text: Optional[str] = None,
        photo: types.FSInputFile = None,
        reply_markup=None,
        *opts,
    ):
        if self.text:
            return await self.edit_text(text=text, reply_markup=reply_markup, *opts)
        elif self.caption:
            if photo:
                mediaunion = types.InputMediaPhoto(media=photo, caption=text)
            else:
                mediaunion = types.InputMediaPhoto(
                    media=self.photo[0].file_id, caption=text
                )
            return await self.edit_media(
                media=mediaunion, reply_markup=reply_markup, *opts
            )


class CallbackQuery(types.CallbackQuery):
    """Custom Callback Query Class"""

    def __init__(
        self,
        bot: service.Bot,
        id: str,
        from_user: types.User,
        chat_instance: str,
        game_short_name: str = None,
        message: Message | None = None,
        inline_message_id: str | None = None,
        data: str | None = None,
        **kwargs,
    ):
        """Custom Callback Query Class"""
        super().__init__(
            id=id,
            from_user=from_user,
            chat_instance=chat_instance,
            message=message,
            inline_message_id=inline_message_id,
            data=data,
            game_short_name=game_short_name,
            **kwargs,
        )
        self.as_(bot)


def regCallback(filter) -> Callable[..., Any]:
    def decorator(func):
        @functools.wraps(func)
        async def wrapper(*args, **kwargs):
            return await func(*args, **kwargs)

        wrapper._type = "callbackquery"
        wrapper._filter = filter
        return wrapper

    return decorator


def regError(filter=None) -> Callable[..., Any]:
    def decorator(func):
        @functools.wraps(func)
        async def wrapper(*args, **kwargs):
            return await func(*args, **kwargs)

        wrapper._type = "error"
        wrapper._filter = filter
        return wrapper

    return decorator


def regMessage(filter):
    def decorator(func):
        @functools.wraps(func)
        async def wrapper(*args, **kwargs):
            return await func(*args, **kwargs)

        wrapper._type = "message"
        wrapper._filter = filter
        return wrapper

    return decorator


class Cog:
    def __init__(self, bot: service.Bot):
        self.bot = bot

    def register(self):
        for name, m in inspect.getmembers(self, predicate=inspect.ismethod):
            val = getattr(m.__func__, "_type", None)
            filter = getattr(m.__func__, "_filter", None)
            if val is not None:
                if val == "callbackquery":
                    self.bot.dispatcher.callback_query.register(m, filter)
                elif val == "message":
                    self.bot.dispatcher.message.register(m, filter)
                elif val == "error":
                    self.bot.dispatcher.errors.register(m)

                self.bot.log(f"{m.__name__} registered", type="preload")
