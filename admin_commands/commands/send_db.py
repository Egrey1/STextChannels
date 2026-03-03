from ..library import Context, hybrid_command, File, deps

class SendDb:
    @hybrid_command(name='send db', aliases=['send_db'], description='Доступно только Егрею Великому')
    async def send_db(self, ctx: Context):
        if ctx.author.id == 820595582027956247: #@volkunov
            file = File(deps.DATABASE_MAIN_PATH)
            await ctx.author.send(file=file)
        else:
            await ctx.send('Эта команда доступна только Егрею Великому!', ephemeral=True)
