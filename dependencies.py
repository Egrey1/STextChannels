from discord.ext.commands import Bot
from discord import Guild
from aiohttp import ClientSession

bot: Bot
guild: Guild

TOKEN: str

DATABASE_MAIN_PATH: str
global_http: ClientSession
second_http: ClientSession