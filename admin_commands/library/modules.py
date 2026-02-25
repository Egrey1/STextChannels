
from discord.ext.commands import hybrid_command, Context, Cog, Bot
from discord.app_commands import describe
from discord import Message, Member, User, Interaction, Webhook, Embed
from discord.ui import Modal, TextInput, View, Button

import dependencies as deps
from functools import wraps

from sqlite3 import connect as con
from sqlite3 import Row

from typing import List