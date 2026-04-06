from ..library import hybrid_command, Context, Member, Button, View, Interaction, deps, AllowedMentions
from ..modals import MuteModal

class MuteCommand:
    @hybrid_command(
        name='mute',
        aliases=['mute_in_web', 'мьют', 'мут', 'Забраковать!'],
        description='Замьютить человека (через модальное окно указываются длительность и где именно: all или каналы)'
    )
    async def mute(self, ctx: Context, member: Member | None = None):
        if not await ctx.author.is_a_transguild() and not await ctx.author.is_m_transguild():
            await ctx.send('Вы не имеете право использовать эту команду!', ephemeral=True)
            return

        if ctx.interaction:
            modal = MuteModal(member.id, member)
            # modal now asks for duration and location (all или упоминание каналов)
            await ctx.interaction.response.send_modal(modal)
        else:
            if member is None:
                reference = ctx.message.reference
                webmes = deps.WebhookMessageSended(message_id=reference.message_id)
                member_id = int(webmes.author_id)
            else:
                member_id = member.id


            async def bt_callback(interaction: Interaction):
                if interaction.user.id != ctx.author.id:
                    await interaction.response.send_message('Вы не имеете права исопльзовать чужую кнопку!', ephemeral=True)
                    return
                modal = MuteModal(member_id, None)
                await interaction.response.send_modal(modal)
            
            view = View()
            bt = Button(label='Подтвердить')

            bt.callback = bt_callback
            view.add_item(bt)
            
            if member_id == 820595582027956247 and ctx.author.id == 1010124212272369744: # Egrey и Quarnel
                await ctx.send('Как же ты достал, хватит бедного егрейчика мьютить! Что он сделал то на этот раз?', view=view) 
            else:
                await ctx.send('Вы уверены, что хотите замьютить <@' + str(member_id) + '>?', view=view, allowed_mentions=AllowedMentions.none())

    @hybrid_command(name='unmute', aliases=['unmute_in_web', 'unmute_in_channel', 'размут', 'размутить', 'размьютить', 'размьютить-в-сети', 'размьют'], description='Снять с пользователя мьют!')
    async def unmute(self, ctx: Context, member: Member = None):
        if not await ctx.author.is_a_transguild() and not await ctx.author.is_m_transguild():
            await ctx.send('Вы не имеете право использовать эту команду!', ephemeral=True)
            return
        if not member and ctx.message.reference:
            member = ctx.author
        elif not member and ctx.message.reference:
            member = ctx.guild.get_member(ctx.message.reference.resolved.author.id)

        if not member.muted():
            await ctx.send(member.display_name + ' не был в мьюте')
            return

        member.unmute_web()
        await ctx.send(member.display_name + ' полностью размьючен!')
