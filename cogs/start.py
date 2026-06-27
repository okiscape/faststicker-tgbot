import cog

class Handler(cog.Cog):
	def __init__(self, bot: cog.Bot):
		super().__init__(bot)

	@cog.regMessage(cog.F.text == "/start")
	async def command(self, message: cog.Message):
		await message.answer("""Welcome to the Fast Sticker Bot!
					   
Use /help to see available commands.
Or /new_pack to quickly create a new sticker pack!""")

def setup(bot: cog.Bot):
	Handler(bot=bot).register()