import asyncio
import time
from collections import OrderedDict
from datetime import datetime


class Filter:
    def __init__(self, column: str, value: any, operator: str = "="):
        self.column: str = column
        self.operator: str = operator

        if value == False:
            self.value: int = 0
        elif value == True:
            self.value = 1
        else:
            self.value: any = value


class AsyncLRUTTLCache:
    def __init__(self, maxsize: int = 1024, ttl: int = 300):
        self.maxsize = maxsize
        self.ttl = ttl
        self.store = OrderedDict()  # key -> (value, expire_ts)
        self.lock = asyncio.Lock()

    async def clear(self):
        async with self.lock:
            self.store.clear()
            # self.store.clear()	del self.store[item]

    async def get(self, key):
        async with self.lock:
            item = self.store.get(key)
            if not item:
                return None
            value, expire = item
            if expire is not None and time.time() > expire:
                # expired
                del self.store[key]
                return None
            # mark as recently used
            self.store.move_to_end(key)
            return value

    async def set(self, key, value):
        async with self.lock:
            if key in self.store:
                del self.store[key]
            self.store[key] = (value, time.time() + self.ttl if self.ttl else None)
            # evict if too many
            while len(self.store) > self.maxsize:
                self.store.popitem(last=False)

    async def resolve(self, key, resolver_coro):
        """Возвращает cached value или вызывает resolver_coro() для получения и сохранения."""
        val = await self.get(key)
        if val is not None:
            return val
        # not cached -> resolve
        value = await resolver_coro()
        if value is not None:
            await self.set(key, value)
        return value


class FiltersGroup:
    def __init__(self, operator: str, filters: list[Filter]):
        """
        Args:
                operator (str): Логический оператор для группы ('AND' или 'OR')
                filters (list[Filter]): Список фильтров в группе
        """
        self.operator: str = operator.upper()
        self.filters: list[Filter] = filters
        if self.operator not in ["AND", "OR"]:
            raise ValueError("Operator must be 'AND' or 'OR'")


class Join:
    def __init__(
        self,
        table: str,
        alias: str = None,
        filters: list[Filter] = [],
        type: str = "INNER JOIN",
    ):
        self.table: str = table
        self.alias: str = alias
        self.type: str = type
        self.filters: list[Filter] = filters


class PaginationResult:
    def __init__(
        self, text: str, buttons: list, page: int, pages: int, offset: int, limit: int
    ):
        self.text: str = text
        self.buttons: list = buttons
        self.page: int = page
        self.pages: int = pages
        self.offset: int = offset
        self.limit: int = limit


class Stickerpack:
    def __init__(self, tgId: int, packName: str, createdAt: int, packTitle: str = ""):
        self.tgId: int = tgId
        self.packName: str = packName
        self.createdAt: datetime = datetime.fromtimestamp(createdAt)
        self.packTitle: str = packTitle
