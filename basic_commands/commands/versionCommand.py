from ..library import hybrid_command, Context, deps

class VersionCommand:
    @hybrid_command(name='version', aliases=['версия'])
    async def version(self, ctx: Context):
        await ctx.send(f'Версия бота: {deps.version}', ephemeral=True)