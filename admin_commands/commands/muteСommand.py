from ..library import hybrid_command, Context, Member, Button, View, Interaction, deps
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
            modal = MuteModal(member.id)
            # modal now asks for duration and location (all или упоминание каналов)
            await ctx.interaction.response.send_modal(modal)
        else:
            if member is None:
                reference = ctx.message.reference
                webmes = deps.WebhookMessageSended(message_id=reference.message_id)
                member = webmes.author_id
            else:
                member = member.id
            member: int


            async def bt_callback(interaction: Interaction):
                if interaction.user.id != ctx.author.id:
                    await interaction.response.send_message('Вы не имеете права исопльзовать чужую кнопку!', ephemeral=True)
                    return
                modal = MuteModal(member)
                await interaction.response.send_modal(modal)
            
            view = View()
            bt = Button(label='Подтвердить')

            bt.callback = bt_callback
            view.add_item(bt)
            await ctx.send('Вы уверены, что хотите замьютить <@' + str(member) + '>?', view=view)

    @hybrid_command(name='unmute', aliases=['unmute_in_web', 'unmute_in_channel', 'размут', 'размутить', 'размьютить', 'размьютить-в-сети', 'размьют'], description='Снять с пользователя мьют!')
    async def unmute(self, ctx: Context, member: Member):
        if not await ctx.author.is_a_transguild() and not await ctx.author.is_m_transguild():
            await ctx.send('Вы не имеете право использовать эту команду!', ephemeral=True)
            return
        member.unmute_web()
        await ctx.send(member.display_name + ' Полностью размьючен!')
