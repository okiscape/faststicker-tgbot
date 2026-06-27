import random
import string

import cog


class Handler(cog.Cog):
    def __init__(self, bot: cog.Bot):
        super().__init__(bot)

    @cog.regMessage(cog.F.text == "/del_pack")
    async def delete_pack_command(self, message: cog.Message, state: cog.FSMContext):

        stickersets = await self.bot.dbm.readStickerpacks(tgId=message.from_user.id)

        if not stickersets:
            return await message.answer(
                "You don't have any sticker packs created!",
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
            """Please, choose the sticker set you want to delete in the keyboard.""",
            reply_markup=keyboard,
        )

        await state.set_state(cog.states.PackDeleteState.packName)

    @cog.regMessage(cog.states.PackDeleteState.packName)
    async def receive_packname(self, message: cog.Message, state: cog.FSMContext):
        pack_name = message.text

        stickersets = await self.bot.dbm.readStickerpacks(
            tgId=message.from_user.id, packName=pack_name
        )

        if not stickersets:
            await message.answer(
                "You don't have a sticker pack with this name! Please, choose a valid sticker pack from the keyboard.",
                reply_markup=cog.aiotypes.ReplyKeyboardRemove(),
            )
            return await state.set_state(cog.states.PackDeleteState.packName)
        pack_to_delete = stickersets[0]

        try:
            tg_stickerset = await self.bot.get_sticker_set(
                name=pack_to_delete.packName
                + "_by_"
                + (await self.bot.get_me()).username
            )
        except Exception as e:
            await message.answer(
                "The sticker pack you are trying to delete does not exist on Telegram! It might have been deleted already.",
                reply_markup=cog.aiotypes.ReplyKeyboardRemove(),
            )
            await self.bot.dbm.deleteStickerpacks(
                tgId=message.from_user.id, packName=pack_to_delete.packName
            )
            await state.clear()
            return

        code = "".join(random.choices(string.ascii_uppercase + string.digits, k=8))

        pack_link = f"https://t.me/addstickers/{tg_stickerset.name}"
        sticker_count = len(tg_stickerset.stickers)

        info = (
            f"<b>Are you sure you want to delete this sticker pack?</b>\n\n"
            f"<b>Title:</b> {tg_stickerset.title}\n"
            f"<b>Name:</b> {tg_stickerset.name}\n"
            f"<b>Stickers count:</b> {sticker_count}\n"
            f"<b>Created:</b> {pack_to_delete.createdAt.strftime('%Y-%m-%d %H:%M:%S')}\n"
            f'<b>Link:</b> <a href="{pack_link}">open pack</a>\n\n'
            f"To confirm deletion, please send the code below:\n"
            f"<i>{code}</i>"
        )

        await state.update_data(confirmCode=code, packName=pack_to_delete.packName)

        await message.answer(
            info,
            reply_markup=cog.aiotypes.ReplyKeyboardRemove(),
        )

        await state.set_state(cog.states.PackDeleteState.confirmCode)

    @cog.regMessage(cog.states.PackDeleteState.confirmCode)
    async def receive_confirmation(self, message: cog.Message, state: cog.FSMContext):
        data = await state.get_data()
        expected_code = data.get("confirmCode")
        pack_name = data.get("packName")

        if message.text != expected_code:
            await message.answer(
                "Invalid code. Deletion cancelled.",
                reply_markup=cog.aiotypes.ReplyKeyboardRemove(),
            )
            await state.clear()
            return

        # delete the sticker pack
        try:
            await self.bot.delete_sticker_set(
                name=pack_name + "_by_" + (await self.bot.get_me()).username
            )
        except Exception as e:
            await message.answer(
                "An error occurred while deleting the sticker pack. Please try again later.",
                reply_markup=cog.aiotypes.ReplyKeyboardRemove(),
            )
            await state.clear()
            return

        await self.bot.dbm.deleteStickerpacks(
            tgId=message.from_user.id, packName=pack_name
        )

        await message.answer(
            f"Your sticker pack '{pack_name}' has been successfully deleted!",
            reply_markup=cog.aiotypes.ReplyKeyboardRemove(),
        )

        await state.clear()


def setup(bot: cog.Bot):
    Handler(bot=bot).register()
