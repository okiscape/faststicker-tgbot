import cog


class Handler(cog.Cog):
    def __init__(self, bot: cog.Bot):
        super().__init__(bot)

    @cog.regMessage(cog.F.text == "/my_packs")
    async def my_packs_command(self, message: cog.Message):
        userpacks = await self.bot.dbm.readStickerpacks(tgId=message.from_user.id)
        if not userpacks:
            await message.reply(
                "You don't have any stickerpacks created with this bot!\nCreate one with /new_pack command!"
            )
            return

        stickerpacksFormatted = []

        for stickerpack in userpacks:
            full_pack_name = (
                stickerpack.packName + "_by_" + (await self.bot.get_me()).username
            )
            try:
                tg_stickerset = await self.bot.get_sticker_set(
                    name=stickerpack.packName
                    + "_by_"
                    + (await self.bot.get_me()).username
                )
            except Exception:
                await self.bot.dbm.deleteStickerpacks(
                    tgId=message.from_user.id, packName=stickerpack.packName
                )
                continue
            stickerpacksFormatted.append(f"""<blockquote><a href=\"https://t.me/addstickers/{full_pack_name}\"><b>{stickerpack.packTitle}</b></a></blockquote>
{len(tg_stickerset.stickers)} stickers""")

        await message.answer(f"""Your stickerpacks:

{"\n\n".join(stickerpacksFormatted)}""")


def setup(bot: cog.Bot):
    Handler(bot=bot).register()
