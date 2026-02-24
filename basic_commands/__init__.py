from .events import *

class BasicCommands(Listener):
    def __init__(self, bot):
        self.bot = bot

async def setup(bot):
    await bot.add_cog(BasicCommands(bot))