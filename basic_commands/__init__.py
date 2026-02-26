from .events import *
from .commands import *

class BasicCommands(Listener, TransguildCommand):
    def __init__(self, bot):
        self.bot = bot

async def setup(bot):
    await bot.add_cog(BasicCommands(bot))