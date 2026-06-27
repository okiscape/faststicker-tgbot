import io

from aiogram import BaseMiddleware, F
from aiogram import methods as aiomethods
from aiogram import types as aiotypes
from aiogram.client.session.middlewares.base import BaseRequestMiddleware
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.types import ErrorEvent, InlineKeyboardButton, InlineKeyboardMarkup
from aiogram.utils import formatting
from colorama import Fore as clr
from PIL import Image

from utils import shortcuts as sh
from utils.cog import CallbackQuery, Cog, Message, regCallback, regMessage
from utils.integrations import databaseMethods
from utils.service import Bot
from utils.stores import config, states, types
