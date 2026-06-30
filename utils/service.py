import asyncio
import datetime
import importlib
import sys

import aiosqlite
from aiogram import Bot as aiBot
from aiogram import Dispatcher
from colorama import Fore

from utils import shortcuts
from utils.integrations import databaseMethods
from utils.stores import config


class Bot(aiBot):
    """Custom Bot Class"""

    def __init__(self):
        """Custom Bot Class"""
        self.config = config
        self.dispatcher = Dispatcher()
        self.db: aiosqlite.Connection = ...
        self.dbm: databaseMethods.DatabaseMethods = ...
        self.sh = shortcuts
        self.logIgnoreTypes = config.logIgnoreTypes
        self.handlers_list = []
        self.startedAt = self.nowdt()
        super().__init__(
            token=config.env.BOT_TOKEN,
            default=config.defaults,
        )

    async def databaseConnect(self):
        self.db = await aiosqlite.connect(self.config.databasePath)
        self.dbm: databaseMethods.DatabaseMethods = databaseMethods.DatabaseMethods(
            self
        )
        return self.db

    def load_cog(self, module_name: str):
        if module_name in sys.modules:
            del sys.modules[module_name]
        module = importlib.import_module(module_name)
        if hasattr(module, "setup"):
            module.setup(self)

    def load_handlers(self, handlers: list[str]):
        self.handlers_list = handlers
        for module_name in handlers:
            try:
                self.load_cog(module_name)
                self.log(f"Module {module_name} loaded", type="modules")
            except Exception as e:
                self.log(f"Error loading {module_name}: {str(e)}", type="error")
                raise e

    def run(self):
        try:

            async def a():
                await self.databaseConnect()
                me = await self.me()
                self.log(
                    f"Logged in as {me.full_name}",
                    f"Username: https://t.me/{me.username}",
                    f"Bot ID: {me.id}",
                    type="global",
                )

                try:
                    # await self.delete_webhook(drop_pending_updates=True)
                    await self.dispatcher.start_polling(self)
                except (asyncio.exceptions.CancelledError, KeyboardInterrupt):
                    self.log("Stop signal recieved", type="internal")
                finally:
                    await self.session.close()
                    self.log("Bot session closed", type="internal")
                    await self.db.close()
                    self.log("Database connection closed", type="internal")

            # self.log("Bot start...", type="internal")

            asyncio.run(a())

        finally:
            self.log("Nothing further remaining to do!", type="global")

    @property
    def datetime(self):
        return datetime.datetime

    def nowdt(self):
        return self.datetime.now(self.config.defaultTimezone)

    def log(self, *args, type=None, **kwargs):
        """
        Types:
                debug
                internal
                autorenewal
                recv
                resp
                preload
                modules
                warn
                ok
                error
                db
                pos
                global
        """
        args = [str(i) for i in list(args)]
        kwargs = [f"{i}: {str(i)}" for i in kwargs]
        if type:
            argTypes = {
                "debug": f"{Fore.YELLOW}- DBG{Fore.RESET}",
                "internal": f"{Fore.CYAN}- INT{Fore.RESET}",
                "autorenewal": f"{Fore.LIGHTGREEN_EX}- REN REM{Fore.RESET}",
                "recv": f"{Fore.LIGHTMAGENTA_EX}< RECV{Fore.RESET}",
                "resp": f"{Fore.LIGHTMAGENTA_EX}> RESP{Fore.RESET}",
                "preload": "- LOAD",
                "modules": f"{Fore.LIGHTBLUE_EX}- MODULES{Fore.RESET}",
                "warn": f"{Fore.RED}~ WR{Fore.RESET}",
                "ok": f"{Fore.CYAN}V OK{Fore.RESET}",
                "error": f"{Fore.LIGHTRED_EX}X ER{Fore.RESET}",
                "db": f"{Fore.LIGHTBLUE_EX}- DB{Fore.RESET}",
                "pos": f"{Fore.LIGHTWHITE_EX}- POS{Fore.RESET}",
                "global": f"{Fore.MAGENTA}- GLOBAL{Fore.RESET}",
            }

            if type in self.logIgnoreTypes:
                return

            args.insert(0, argTypes[type.lower()])
        time = self.nowdt().strftime("%H:%M:%S.%f")[:-3]
        datetimeformat = self.nowdt().strftime(f"%d/%m/%Y {time} %Z")
        print(f"[{datetimeformat}] {(' | '.join(args + kwargs)[:1000])}")
