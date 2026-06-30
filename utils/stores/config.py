import os

from dotenv import load_dotenv

load_dotenv()

import pytz
from aiogram.client.default import DefaultBotProperties

defaults = DefaultBotProperties(parse_mode="HTML", link_preview_is_disabled=True)
databasePath = "utils/base.db"

REPO = "okiscape/faststicker-tgbot"
REPO_URL = f"https://github.com/{REPO}"
GITHUB_API_URL = f"https://api.github.com/repos/{REPO}"

defaultTimezone = pytz.timezone("Europe/Moscow")

logIgnoreTypes = ["preload"]


class env:
    BOT_TOKEN = os.environ.get("BOT_TOKEN")


if not env.BOT_TOKEN:
    print("BOT_TOKEN was not found!!!")
    exit(1)
