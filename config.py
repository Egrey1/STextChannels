import dependencies as deps
from discord.ext.commands import Bot
from discord import Intents
from dotenv import load_dotenv
from os import getenv
import aiohttp

def firstConfig():
    load_dotenv()

    deps.bot = deps.Bot(command_prefix="$", intents=Intents.all())
    deps.TOKEN = getenv('TOKEN') # TOKEN HERE

    deps.DATABASE_MAIN_PATH = 'databases/main.db'


async def secondConfig():
    deps.global_http = aiohttp.ClientSession()
    deps.second_http = aiohttp.ClientSession()
    deps.guild = await deps.bot.fetch_guild(1473038842704429180)