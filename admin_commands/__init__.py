from .library import Cog, Bot
from .commands import AddCommand, MuteCommand, SendDb

class AdminCog(Cog, AddCommand, MuteCommand, SendDb):
    def __init__(self, bot):
        super().__init__()
        self.bot = bot

async def setup(bot: Bot):
    await bot.add_cog(AdminCog(bot))