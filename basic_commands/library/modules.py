from discord.ext.commands import Context, Cog

from discord import TextChannel, Message, Webhook

from aiohttp import ClientSession

from sqlite3 import connect as con
from sqlite3 import Row

import dependencies as deps