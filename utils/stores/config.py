from dotenv import dotenv_values

_env = dotenv_values()

import pytz
from aiogram.client.default import DefaultBotProperties

defaults = DefaultBotProperties(parse_mode="HTML", link_preview_is_disabled=True)
databasePath = "utils/base.db"

defaultTimezone = pytz.timezone("Europe/Moscow")

logIgnoreTypes = ["preload"]


class env:
    BOT_TOKEN = _env["BOT_TOKEN"]
