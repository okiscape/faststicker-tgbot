import cog


class PrivateChatCheck(cog.BaseMiddleware):
    def __init__(self, bot: cog.Bot):
        self.bot = bot

    async def __call__(self, handler, event, data):
        if isinstance(event, cog.aiotypes.Message):
            if event.chat.type != "private":
                return
        return await handler(event, data)


class MessageMiddleware(cog.BaseMiddleware):
    def __init__(self, bot: cog.Bot):
        self.bot = bot

    async def __call__(self, handler, event, data):
        try:
            if isinstance(event, cog.aiotypes.Message):
                event = cog.Message(bot=self.bot, **event.__dict__)

                if self.bot.startedAt.timestamp() > event.date.timestamp():
                    return

                if event.text != None:
                    logState = []
                    # storage = data.get("")
                    state = data.get("state")
                    if state:
                        stateData = await state.get_data()
                        logState.append(f"StateData: {stateData}")

                    rawstate = data.get("raw_state")
                    if rawstate:
                        logState.append(f"RawState: {rawstate}")

                    self.bot.log(
                        f"ID:{event.from_user.id}",
                        f"{cog.clr.LIGHTYELLOW_EX}TEXT{cog.clr.RESET}",
                        f'Text: "{event.html_text}"',
                        *logState,
                        type="recv",
                    )

                    if state:
                        if event.text == "/cancel":
                            await event.reply("Action cancelled.")
                            await state.clear()
                            return

        except Exception as e:
            raise e

        return await handler(event, data)


class CallbacksMiddleware(cog.BaseMiddleware):
    def __init__(self, bot: cog.Bot):
        self.bot = bot

    async def __call__(self, handler, event, data):
        try:
            if isinstance(event, cog.aiotypes.CallbackQuery):
                event = cog.CallbackQuery(
                    bot=self.bot,
                    id=event.id,
                    from_user=event.from_user,
                    chat_instance=event.chat_instance,
                    game_short_name=event.game_short_name,
                    message=event.message,
                    data=event.data,
                    inline_message_id=event.inline_message_id,
                )
                logState = []
                state = data.get("state")
                if state:
                    stateData = await state.get_data()
                    logState.append(f"StateData: {stateData}")

                rawstate = data.get("raw_state")
                if rawstate:
                    logState.append(f"RawState: {rawstate}")

                self.bot.log(
                    f"ID:{event.from_user.id}",
                    f"{cog.clr.LIGHTYELLOW_EX}CALLBACK QUERY{cog.clr.RESET}",
                    f'Data:"{event.data}"',
                    *logState,
                    type="recv",
                )

        except Exception as e:
            raise e

        try:
            return await handler(event, data)
        except Exception as exc:
            cq: cog.CallbackQuery | None = None
            if type(event) == cog.CallbackQuery:
                cq = event

                if "message is not modified" in str(exc).lower():
                    return await cq.answer(
                        "Text message is up to date.", show_alert=True
                    )

                try:
                    await cq.answer("An error occurred", show_alert=False)
                    raise exc
                except Exception:
                    pass

            raise exc


class RequestLogging(cog.BaseRequestMiddleware):
    def __init__(self, bot: cog.Bot):
        self.bot = bot
        self.ignore_methods = [
            cog.aiomethods.get_me.GetMe,
            cog.aiomethods.get_updates.GetUpdates,
            cog.aiomethods.delete_webhook.DeleteWebhook,
            cog.aiomethods.answer_callback_query.AnswerCallbackQuery,
        ]
        self.lastLog = self.bot.nowdt()

    async def __call__(self, make_request, bot, method):
        if type(method) not in self.ignore_methods:
            chatId = "!! WITHOUT ID"
            if getattr(method, "chat_id", None):
                chatId = f"ID:{method.chat_id}"
            args = []

            if hasattr(method, "text"):
                args.append(f'Text: "{method.text}"')
            if hasattr(method, "media") or hasattr(method, "caption"):
                caption = ""
                if hasattr(method, "caption"):
                    caption = method.caption
                elif hasattr(method.media, "caption"):
                    caption = method.media.caption
                args.append(f'Caption: "{caption}"')

            self.bot.log(
                chatId,
                f"{cog.clr.LIGHTYELLOW_EX}{str(type(method)).split('.')[-1][:-2].upper()}{cog.clr.RESET}",
                *args,
                type="resp",
            )
        try:
            return await make_request(bot, method)
        except Exception as e:
            raise e


class CastMiddleware(cog.BaseMiddleware):
    def __init__(self, bot: cog.Bot):
        self.bot = bot

    async def __call__(self, handler, event, data):
        if isinstance(event, cog.aiotypes.Message):
            event = cog.Message(bot=self.bot, **event.__dict__)
        elif isinstance(event, cog.aiotypes.CallbackQuery):
            msg = None
            if event.message:
                msg = cog.Message(bot=self.bot, **event.message.__dict__)

            event = cog.CallbackQuery(
                bot=self.bot,
                id=event.id,
                from_user=event.from_user,
                chat_instance=event.chat_instance,
                game_short_name=event.game_short_name,
                message=msg,
                data=event.data,
                inline_message_id=event.inline_message_id,
            )
        return await handler(event, data)


def setup(bot: cog.Bot):
    bot.dispatcher.callback_query.outer_middleware(CastMiddleware(bot))
    bot.dispatcher.callback_query.middleware(CallbacksMiddleware(bot))
    bot.dispatcher.message.outer_middleware(CastMiddleware(bot))
    bot.dispatcher.message.outer_middleware(MessageMiddleware(bot))
    bot.dispatcher.message.middleware(PrivateChatCheck(bot))
    bot.session.middleware(RequestLogging(bot))
