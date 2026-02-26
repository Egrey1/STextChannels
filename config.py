import dependencies as deps
from discord.ext.commands import Bot
from dotenv import load_dotenv
from os import getenv
import aiohttp
import discord as ds
import classes as cls

def firstConfig():
    load_dotenv()

    deps.intents = ds.Intents.all()

    deps.bot = deps.Bot(command_prefix="$", intents=deps.intents)
    deps.TOKEN = getenv('TOKEN') # TOKEN HERE

    deps.DATABASE_MAIN_PATH = 'databases/main.db'

    ds.Member.is_a_transguild = cls.NewMember.is_a_transguild
    ds.Member.from_capital = cls.NewMember.from_capital

    ds.User.is_a_transguild = cls.NewUser.is_a_transguild
    ds.User.from_capital = cls.NewUser.from_capital


async def secondConfig():
    deps.global_http = aiohttp.ClientSession()
    deps.second_http = aiohttp.ClientSession()
    deps.capital = await deps.bot.fetch_guild(1473038842704429180)
    deps.a_transguild = deps.capital.get_role(1476193110592716880)