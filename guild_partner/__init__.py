from .library import Cog, Bot
from .commands import GuildPartners

class GuildPartnerCog(Cog, GuildPartners):
    def __init__(self, bot: Bot):
        self.bot = bot

async def setup(bot: Bot):
    await bot.add_cog(GuildPartnerCog(bot))