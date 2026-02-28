import dependencies as deps
from discord.ext.commands import Bot
from dotenv import load_dotenv
from os import getenv
import aiohttp
import discord as ds
import classes as cls
import logging

def firstConfig():
    load_dotenv()

    deps.intents = ds.Intents.all()

    deps.PREFIX = ('stc ', 'stc.', 'stc. ', '$$', '$$ ', ';;', ';; ')

    deps.bot = deps.Bot(command_prefix=deps.PREFIX, intents=deps.intents, help_command=None)
    deps.TOKEN = getenv('TOKEN') # TOKEN HERE

    deps.DATABASE_MAIN_PATH = 'databases/main.db'

    ds.Member.is_a_transguild = cls.NewMember.is_a_transguild
    ds.Member.from_capital = cls.NewMember.from_capital
    ds.Member.is_m_transguild = cls.NewMember.is_m_transguild

    ds.User.is_a_transguild = cls.NewUser.is_a_transguild
    ds.User.from_capital = cls.NewUser.from_capital
    ds.User.is_m_transguild = cls.NewUser.is_m_transguild


    ds.TextChannel.get_all_webs = cls.New_TextChannel.get_all_webs

    deps.Web = cls.Web

    logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')


async def secondConfig():
    deps.global_http = aiohttp.ClientSession()
    deps.second_http = aiohttp.ClientSession()
    deps.capital = await deps.bot.fetch_guild(1473038842704429180)
    deps.a_transguild = await deps.capital.fetch_role(1476193110592716880)
    deps.m_transguild = await deps.capital.fetch_role(1476633956945363196)