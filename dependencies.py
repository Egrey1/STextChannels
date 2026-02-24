from discord.ext.commands import Bot
from aiohttp import ClientSession

bot: Bot
TOKEN: str

DATABASE_MAIN_PATH: str
global_http: ClientSession