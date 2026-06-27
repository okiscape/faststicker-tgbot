from aiogram.fsm.state import State, StatesGroup


class PackCreationState(StatesGroup):
    title: str = State()
    packName: str = State()
    stickersAdd = State()
    stickersAddStickerEmojis = State()
    stickers: list = State()


class PackDeleteState(StatesGroup):
    packName: str = State()
    confirmCode: str = State()


class AddStickerState(StatesGroup):
    packToAdd: str = State()
    waitingForSticker = State()
    stickersAddStickerEmojis = State()


class CopyPackState(StatesGroup):
    sourcePackName: str = State()
    newTitle: str = State()
    newPackName: str = State()
