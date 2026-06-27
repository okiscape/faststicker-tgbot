import cog


class Handler(cog.Cog):
    def __init__(self, bot: cog.Bot):
        super().__init__(bot)

    @cog.regMessage(cog.F.text == "/start")
    async def startcommand(self, message: cog.Message):
        await message.answer("""Welcome to the Fast Sticker Bot!

Use /help to see available commands
Use /about to see info about this bot
Or /new_pack to quickly create a new sticker pack!""")

    @cog.regMessage(cog.F.text == "/about")
    async def aboutcommand(self, message: cog.Message):
        await message.answer("""About Fast Sticker Bot!

This bot created for simplier stickerpack creation using: already existing stickers, gifs, and media from your gallery for simple sticker creation.
This bot will convert your media to needed format for telegram to save it in your stickerpack.

<a href="https://github.com/okiscape/faststicker-bot">Sources</a>""")

    @cog.regMessage(cog.F.text == "/help")
    async def helpcommand(self, message: cog.Message):
        await message.answer("""My commands:

/new_pack - create new pack
/del_pack - delete your existing pack
/my_packs - see your packs
/add_sticker - start adding stickers process
 - /copy_emoji - toggles emoji copying from existing stickers
/about - see info about this bot and sources""")


def setup(bot: cog.Bot):
    Handler(bot=bot).register()
