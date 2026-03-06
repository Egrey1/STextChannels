from discord.ext.commands import hybrid_command, Context, Cog, has_permissions
from discord.app_commands import describe
from discord import Member, Guild, Interaction, ButtonStyle, SelectOption, Interaction, TextStyle
from discord.ui import Modal, View, Button, TextInput, Select

import logging

import dependencies as deps

from random import randint

from typing import List