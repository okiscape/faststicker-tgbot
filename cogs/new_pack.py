import cog
from utils.integrations.video_convert import convert_to_webm


class Handler(cog.Cog):
    def __init__(self, bot: cog.Bot):
        super().__init__(bot)

    @cog.regMessage(cog.F.text == "/new_pack")
    async def command(self, message: cog.Message, state: cog.FSMContext):
        await message.answer("""Let's create a new sticker pack!

First, send me title for your new sticker pack, like 'My Cool Stickers'.""")

        await state.set_state(cog.states.PackCreationState.title)

    @cog.regMessage(cog.states.PackCreationState.title)
    async def receive_title(self, message: cog.Message, state: cog.FSMContext):
        title = message.text
        await state.update_data(title=title)
        await message.answer(
            "Nice title! Now, send me your link to the sticker pack, like 'my_cool_stickers'\n*\"_by_faststicker_bot\" will be added in the end(that is telegram requirement!!)."
        )
        await state.set_state(cog.states.PackCreationState.packName)

    @cog.regMessage(filter=cog.states.PackCreationState.packName)
    async def receive_packname(self, message: cog.Message, state: cog.FSMContext):
        pack_name = message.text
        if not pack_name.isalnum() and "_" not in pack_name:
            await message.answer(
                "Pack name can only contain letters, numbers and underscores! Please send me a valid pack name."
            )
            return await state.set_state(cog.states.PackCreationState.packName)

        try:
            print(pack_name + "_by_" + (await self.bot.get_me()).username)
            stickerset = await self.bot.get_sticker_set(
                name=pack_name + "_by_" + (await self.bot.get_me()).username
            )
            print(stickerset)
            await message.answer(
                "A sticker pack with this name already exists! Please send me a different link/name for your sticker pack."
            )
            return
        except Exception:
            pass
        await state.update_data(packName=pack_name)

        await message.answer(
            f"Great! Your new sticker pack '{pack_name}' will be created.\nPlease send me the sticker image and the emojis, that will be associated with this sticker.\nI'll convert it to needed format and resolution!."
        )
        await state.set_state(cog.states.PackCreationState.stickersAdd)

    @cog.regMessage(cog.states.PackCreationState.stickersAdd)
    async def receive_sticker(self, message: cog.Message, state: cog.FSMContext):

        if message.text == "/done":
            return await self.finalize_pack(message=message, state=state)

        if (
            not message.sticker
            and not message.photo
            and not message.document
            and not message.animation
        ):
            await message.answer("Please send me a valid sticker or image!")
            return

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
            sticker_io = cog.io.BytesIO(file_bytes.read())
            sticker_io.seek(0)
            im = cog.sh.fitImage(sticker_io, max_size=512)
            newio = cog.io.BytesIO()
            im.save(newio, format="PNG")
            newio.seek(0)
            sticker_data = newio.getvalue()
        elif message.document:
            file_info = await self.bot.get_file(message.document.file_id)
            file_bytes = await self.bot.download_file(file_info.file_path)
            mime = getattr(message.document, "mime_type", None)
            fname = (
                message.document.file_name.lower() if message.document.file_name else ""
            )
            if mime == "application/x-tgsticker" or fname.endswith(".tgs"):
                sticker_format = "animated"
                filename = "sticker.tgs"
                sticker_data = file_bytes.read()
            elif mime == "video/mp4" or fname.endswith(".mp4"):
                sticker_format = "video"
                filename = "sticker.webm"
                sticker_data = file_bytes.read()
            else:
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
                f"Sticker added!\nYou can send me more stickers to add to the pack, or send /done when you are finished."
            )
        else:
            await state.update_data(
                current_sticker=sticker_data,
                current_format=sticker_format,
                current_filename=filename,
            )
            await message.answer("Please provide emojis for this sticker.")
            await state.set_state(cog.states.PackCreationState.stickersAddStickerEmojis)

    @cog.regMessage(cog.states.PackCreationState.stickersAddStickerEmojis)
    async def receive_sticker_sticker_emojis(
        self, message: cog.Message, state: cog.FSMContext
    ):

        if not cog.sh.is_emoji(message.text):
            await message.answer("Please, send only emojis!")
            return

        emojis = list(message.text)

        data = await state.get_data()
        stickers = data.get("stickers", [])
        current_sticker = data.get("current_sticker")
        current_format = data.get("current_format", "static")
        current_filename = data.get("current_filename", "sticker.png")

        if not current_sticker:
            await message.answer(
                "Error: no sticker found. Please send a sticker again."
            )
            return await state.set_state(cog.states.PackCreationState.stickersAdd)

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
            f"Sticker added!\nYou can send me more stickers to add to the pack, or send /done when you are finished."
        )
        await state.set_state(cog.states.PackCreationState.stickersAdd)

    async def finalize_pack(self, message: cog.Message, state: cog.FSMContext):

        data = await state.get_data()
        title = data.get("title")
        pack_name = data.get("packName")
        stickers = data.get("stickers", [])

        stickerlist = []

        for sticker in stickers:
            sticker_data = sticker["sticker"]
            if isinstance(sticker_data, cog.io.BytesIO):
                sticker_data = sticker_data.getvalue()

            if isinstance(sticker_data, str):
                stickerlist.append(
                    cog.aiotypes.InputSticker(
                        sticker=sticker_data,
                        format=sticker.get("format", "static"),
                        emoji_list=sticker["emojis"],
                    )
                )
            else:
                stickerlist.append(
                    cog.aiotypes.InputSticker(
                        sticker=cog.aiotypes.BufferedInputFile(
                            file=sticker_data,
                            filename=sticker.get("filename", "sticker.png"),
                        ),
                        format=sticker.get("format", "static"),
                        emoji_list=sticker["emojis"],
                    )
                )

        try:
            stickerset_created = await self.bot.create_new_sticker_set(
                user_id=message.from_user.id,
                name=pack_name + "_by_" + (await self.bot.get_me()).username,
                title=title,
                stickers=stickerlist,
            )

        except Exception as e:
            await message.answer(
                f"An error occurred while creating the sticker pack!\nPlease, check the log."
            )
            await state.clear()
            raise e

        await message.answer(
            f"Sticker pack '{title}' created successfully!\nYou can add it from here: t.me/addstickers/{pack_name}_by_{(await self.bot.get_me()).username}"
        )

        await self.bot.dbm.createStickerpack(
            tgId=message.from_user.id,
            packName=pack_name,
            packTitle=title,
            createdAt=cog.sh.getNowDTTS(),
        )

        await state.clear()


def setup(bot: cog.Bot):
    Handler(bot=bot).register()
