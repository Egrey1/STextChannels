from .commands import *
from .library import Cog

class Economic(AddMoneyCommand, ShopCommand, Cog, ItemsCommands):
    def __init__(self, bot):
        super().__init__()
        self.bot = bot

async def setup(bot):
    await bot.add_cog(Economic(bot))