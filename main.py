import cog

bot = cog.Bot()

bot.load_handlers(
    handlers=[
        "cogs.start",
        "cogs.new_pack",
        "cogs.del_pack",
        "cogs.my_packs",
        "cogs.add_sticker",
        "cogs.middlewares",
    ]
)

bot.run()
