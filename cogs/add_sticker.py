import cog
from utils.integrations.video_convert import convert_to_webm


class Handler(cog.Cog):
    def __init__(self, bot: cog.Bot):
        super().__init__(bot)

    @cog.regMessage(cog.F.text == "/add_sticker")
    async def command(self, message: cog.Message, state: cog.FSMContext):
        stickersets = await self.bot.dbm.readStickerpacks(tgId=message.from_user.id)

        if not stickersets:
            return await message.answer(
                "You don't have any sticker packs created! Use /new_pack to create a new sticker pack.",
                reply_markup=cog.aiotypes.ReplyKeyboardRemove(),
            )

        buttons = []

        for pack in stickersets:
            buttons.append(cog.aiotypes.KeyboardButton(text=pack.packName))

        buttons = [buttons[i : i + 2] for i in range(0, len(buttons), 2)]

        keyboard = cog.aiotypes.ReplyKeyboardMarkup(
            keyboard=buttons, one_time_keyboard=True, resize_keyboard=True
        )

        await message.answer(
            """Please, choose the sticker set you want to add stickers to from the keyboard.""",
            reply_markup=keyboard,
        )

        await state.set_state(cog.states.AddStickerState.packToAdd)

    @cog.regMessage(cog.states.AddStickerState.packToAdd)
    async def receive_packnamet(self, message: cog.Message, state: cog.FSMContext):
        pack_name = message.text
        full_pack_name = pack_name + "_by_" + (await self.bot.get_me()).username
        await message.answer(
            f'Please send me the sticker image you want to add to your <a href="https://t.me/addstickers/{full_pack_name}">pack</a>, along with the emojis in the caption.\n(use /copy_emoji to copy emojis from existing stickers!)'
        )
        await state.update_data(packToAdd=pack_name)
        await state.set_state(cog.states.AddStickerState.waitingForSticker)

    @cog.regMessage(cog.states.AddStickerState.stickersAddStickerEmojis)
    async def receive_sticker_sticker_emojisa(
        self, message: cog.Message, state: cog.FSMContext
    ):
        if cog.sh.is_emoji(message.text) == False:
            await message.answer("Please, send only emojis in the message!")
            return await state.set_state(
                cog.states.AddStickerState.stickersAddStickerEmojis
            )

        emojis = list(message.text)
        data = await state.get_data()
        stickers = data.get("stickers", [])
        current_sticker = data.get("current_sticker")
        current_format = data.get("current_format", "static")
        current_filename = data.get("current_filename", "sticker.png")

        if not current_sticker:
            await message.answer(
                "Error: sticker for this emojis was not found, send the sticker again."
            )
            return await state.set_state(cog.states.AddStickerState.waitingForSticker)

        stickers.append(
            {
                "emojis": emojis,
                "sticker": current_sticker,
                "format": current_format,
                "filename": current_filename,
            }
        )
        await state.update_data(
            stickers=stickers,
            current_sticker=None,
            current_format=None,
            current_filename=None,
        )

        await message.answer(
            f"Sticker added to the pack!\nYou can send me more stickers to add to the pack, or send /done when you are finished."
        )
        await state.set_state(cog.states.AddStickerState.waitingForSticker)

    @cog.regMessage(cog.states.AddStickerState.waitingForSticker)
    async def receive_stickera(self, message: cog.Message, state: cog.FSMContext):
        if message.text == "/copy_emoji":
            data = await state.get_data()
            new_val = not data.get("copy_emoji", False)
            await state.update_data(copy_emoji=new_val)
            status = "enabled" if new_val else "disabled"
            await message.answer(
                f"Copy emoji mode {status}! Emojis from Telegram stickers will be copied automatically."
                if new_val
                else f"Copy emoji mode {status}."
            )
            return

        if message.text == "/done":
            return await self.finalize_pack(message, state)

        if (
            not message.sticker
            and not message.photo
            and not message.document
            and not message.animation
        ):
            await message.answer("Please send me a valid sticker or image!")
            return

        data = await state.get_data()
        copy_emoji = data.get("copy_emoji", False)

        sticker_data = None
        sticker_format = "static"
        filename = "sticker.png"

        if message.sticker:
            if message.sticker.is_video:
                sticker_format = "video"
                filename = "sticker.webm"
            elif message.sticker.is_animated:
                sticker_format = "animated"
                filename = "sticker.tgs"
            sticker_data = message.sticker.file_id
        elif message.document:
            file_info = await self.bot.get_file(message.document.file_id)
            file_bytes = await self.bot.download_file(file_info.file_path)
            mime = getattr(message.document, "mime_type", None)
            fname = (
                message.document.file_name.lower() if message.document.file_name else ""
            )
            print(fname, mime)
            if mime == "video/mp4" or fname.endswith(".mp4"):
                try:
                    sticker_data = convert_to_webm(file_bytes.read())
                    sticker_format = "video"
                    filename = "sticker.webm"
                except Exception as e:
                    await message.answer(f"Failed to convert GIF to video sticker: {e}")
                    return
            elif mime == "application/x-tgsticker" or fname.endswith(".tgs"):
                sticker_format = "animated"
                filename = "sticker.tgs"
                sticker_data = file_bytes.read()
            else:
                sticker_format = "static"
                filename = "sticker.png"
                sticker_io = cog.io.BytesIO(file_bytes.read())
                sticker_io.seek(0)
                im = cog.sh.fitImage(sticker_io, max_size=512)
                newio = cog.io.BytesIO()
                im.save(newio, format="PNG")
                newio.seek(0)
                sticker_data = newio.getvalue()
        elif message.animation:
            file_info = await self.bot.get_file(message.animation.file_id)
            file_bytes = await self.bot.download_file(file_info.file_path)
            try:
                sticker_data = convert_to_webm(file_bytes.read(), suffix=".mp4")
                sticker_format = "video"
                filename = "sticker.webm"
            except Exception as e:
                await message.answer(
                    f"Failed to convert animation to video sticker: {e}"
                )
                return
        elif message.photo:
            photo = message.photo[-1]
            file_info = await self.bot.get_file(photo.file_id)
            file_bytes = await self.bot.download_file(file_info.file_path)
            sticker_format = "static"
            filename = "sticker.png"
            sticker_io = cog.io.BytesIO(file_bytes.read())
            sticker_io.seek(0)
            im = cog.sh.fitImage(sticker_io, max_size=512)
            newio = cog.io.BytesIO()
            im.save(newio, format="PNG")
            newio.seek(0)
            sticker_data = newio.getvalue()

        if message.caption:
            emojis = list(message.caption)
            data = await state.get_data()
            stickers = data.get("stickers", [])
            stickers.append(
                {
                    "emojis": emojis,
                    "sticker": sticker_data,
                    "format": sticker_format,
                    "filename": filename,
                }
            )
            await state.update_data(stickers=stickers)
            await message.answer(
                f"Sticker added to the pack!\nYou can send me more stickers to add to the pack, or send /done when you are finished."
            )
        elif copy_emoji and message.sticker and message.sticker.emoji:
            emojis = message.sticker.emoji
            data = await state.get_data()
            stickers = data.get("stickers", [])
            stickers.append(
                {
                    "emojis": emojis,
                    "sticker": sticker_data,
                    "format": sticker_format,
                    "filename": filename,
                }
            )
            await state.update_data(stickers=stickers)
            await message.answer(
                f"Sticker added to the pack with emojis: {' '.join(emojis)}!\nYou can send me more stickers to add to the pack, or send /done when you are finished."
            )
        else:
            await state.update_data(
                current_sticker=sticker_data,
                current_format=sticker_format,
                current_filename=filename,
            )
            await message.reply("Please, provide emojis now for this sticker.")
            return await state.set_state(
                cog.states.AddStickerState.stickersAddStickerEmojis
            )

    async def finalize_pack(self, message: cog.Message, state: cog.FSMContext):
        data = await state.get_data()
        pack_name = data.get("packToAdd")
        stickers = data.get("stickers", [])

        pack_full_name = pack_name + "_by_" + (await self.bot.get_me()).username

        if not stickers:
            await message.answer(
                "You haven't added any stickers to the pack yet! Please send me at least one sticker before finalizing."
            )
            return await state.set_state(cog.states.AddStickerState.waitingForSticker)

        try:
            tg_stickerset = await self.bot.get_sticker_set(name=pack_full_name)
        except Exception as e:
            print(e)
            await message.answer(
                "The sticker pack you are trying to add stickers to does not exist on Telegram! It might have been deleted."
            )
            await state.clear()
            return

        await message.reply("Adding stickers to the pack...")

        for sticker in stickers:
            sticker_data = sticker["sticker"]
            sticker_format = sticker.get("format", "static")
            filename = sticker.get("filename", "sticker.png")

            try:
                if isinstance(sticker_data, str):
                    input_sticker = cog.aiotypes.InputSticker(
                        sticker=sticker_data,
                        format=sticker_format,
                        emoji_list=sticker["emojis"],
                    )
                else:
                    input_sticker = cog.aiotypes.InputSticker(
                        sticker=cog.aiotypes.BufferedInputFile(
                            sticker_data, filename=filename
                        ),
                        format=sticker_format,
                        emoji_list=sticker["emojis"],
                    )
                await self.bot.add_sticker_to_set(
                    user_id=message.from_user.id,
                    name=pack_full_name,
                    sticker=input_sticker,
                )
            except Exception as e:
                await message.answer(f"Error adding sticker: {e}")
                raise e

        await message.answer(
            f'Your stickers have been successfully added to the pack "<a href="https://t.me/addstickers/{pack_full_name}">{pack_name}</a>"!',
            reply_markup=cog.aiotypes.ReplyKeyboardRemove(),
        )

        await state.clear()


def setup(bot: cog.Bot):
    Handler(bot=bot).register()
