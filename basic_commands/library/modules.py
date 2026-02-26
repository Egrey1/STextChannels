from discord.ext.commands import Context, Cog, hybrid_command
from discord import TextChannel, Message, Webhook, AllowedMentions, Embed

from aiohttp import ClientSession

from sqlite3 import connect as con
from sqlite3 import Row

import dependencies as deps

from typing import List