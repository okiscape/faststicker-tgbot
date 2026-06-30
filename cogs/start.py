import aiohttp

import cog
from utils.stores.config import REPO_URL


class Handler(cog.Cog):
    def __init__(self, bot: cog.Bot):
        super().__init__(bot)
        self._githubCache = cog.types.AsyncLRUTTLCache(maxsize=10, ttl=300)

    async def get_latest_commit(self):
        async def _fetch():
            try:
                async with aiohttp.ClientSession() as session:
                    async with session.get(
                        f"{self.bot.config.GITHUB_API_URL}/commits?per_page=1",
                        timeout=aiohttp.ClientTimeout(total=10),
                    ) as resp:
                        if resp.status != 200:
                            return None
                        data = await resp.json()
            except Exception:
                return None

            if not data or not isinstance(data, list) or len(data) == 0:
                return None
            commit = data[0]
            sha = commit.get("sha", "")[:7]
            committer = commit.get("commit", {}).get("committer", {})
            date = committer.get("date", "")[:10]
            message = commit.get("commit", {}).get("message", "").split("\n")[0]
            return {"sha": sha, "date": date, "message": message}

        return await self._githubCache.resolve("latest_commit", _fetch)

    @cog.regMessage(cog.F.text == "/start")
    async def startcommand(self, message: cog.Message):
        await message.answer("""Welcome to the Fast Sticker Bot!

Use /help to see available commands
Use /about to see info about this bot
Or /new_pack to quickly create a new sticker pack!""")

    @cog.regMessage(cog.F.text == "/about")
    async def aboutcommand(self, message: cog.Message):
        commit = await self.get_latest_commit()
        committed = ""
        if commit:
            committed += (
                f"\n<pre>Latest commit: <code>{commit['sha']}</code> ({commit['date']})"
                f"\nMessage: {commit['message']}</pre>"
            )

        output = f"""About this bot

This bot created for simplier stickerpack creation using: already existing stickers, gifs, and media from your gallery.
This bot will convert your media to needed format for telegram to save it in your stickerpack.
{committed}
<a href="{REPO_URL}">Sources</a>"""
        await message.answer(output)

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
