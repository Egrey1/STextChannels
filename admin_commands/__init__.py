from .library import Cog, Bot
from .commands import AddCommand

class AdminCog(Cog, AddCommand):
    def __init__(self, bot):
        super().__init__()
        self.bot = bot

async def setup(bot: Bot):
    await bot.add_cog(AdminCog(bot))