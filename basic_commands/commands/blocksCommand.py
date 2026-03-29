from ..library import hybrid_command, Context, Member, deps
class BlocksCommand:
    
    @hybrid_command(name='block', aliases=['блок', 'заблокировать'], description='Блокирует пользователя')
    async def block(self, ctx: Context, member: Member = None):
        member = member.id if member is not None else deps.WebhookMessageSended(message_id=ctx.message.reference.message_id).author_id if ctx.message.reference else None
        if member is None:
            await ctx.send('Вы не указали пользователя!', ephemeral=True)
            return
        
        ctx.author.add_blocked_by(ctx.author.id, member)
        await ctx.send('Пользователь <@' + str(member) + '> успешно заблокирован!', delete_after=30)
    
    @hybrid_command(name='unblock', aliases=['разблокировать'], description='Разблокирует пользователя')
    async def unblock(self, ctx: Context, member: Member = None):
        member = member.id if member is not None else deps.WebhookMessageSended(message_id=ctx.message.reference.message_id).author_id if ctx.message.reference else None
        if member is None:
            await ctx.send('Вы не указали пользователя!', ephemeral=True)
            return
        
        ctx.author.remove_blocked_by(ctx.author.id, member)
        await ctx.send('Пользователь <@' + str(member) + '> успешно разблокирован!', delete_after=30)