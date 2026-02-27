from discord.ext.commands import Bot
from discord import Guild, Role, Intents
from aiohttp import ClientSession
from typing import Tuple

bot: Bot
intents: Intents
capital: Guild
PREFIX: Tuple[str]

TOKEN: str

DATABASE_MAIN_PATH: str
global_http: ClientSession
second_http: ClientSession

a_transguild: Role
m_transguild: Role

class Web:
    ...