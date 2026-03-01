from ..library import hybrid_command, Context, Member, Button, View, Interaction
from ..modals import MuteModal

class MuteCommand:
    @hybrid_command(
        name='mute',
        aliases=['mute_in_web', 'мьют', 'мут', 'Забраковать!'],
        description='Замьютить человека в сети или канале(пока недоступно)'
    )
    async def mute(self, ctx: Context, member: Member):
        if not ctx.author.is_a_transguild() and not ctx.author.is_m_transguild():
            await ctx.send('Вы не имеете право использовать эту команду!', ephemeral=True)
            return

        if ctx.interaction:
            modal = MuteModal(member)
            ctx.interaction.response.send_modal(modal)
        else:
            async def bt_callback(interaction: Interaction):
                if interaction.user.id != ctx.author.id:
                    await interaction.response.send_message('Вы не имеете права исопльзовать чужую кнопку!', ephemeral=True)
                    return
                modal = MuteModal(member)
                interaction.response.send_modal(modal)
            
            view = View()
            bt = Button(label='Подтвердить')

            bt.callback = bt_callback
            view.add_item(bt)
            await ctx.send('Вы уверены, что хотите замьютить ' + member.mention + '?', view=view)

    @hybrid_command(name='unmute', aliases=['unmute_in_web', 'unmute_in_channel', 'размут', 'размутить', 'размьютить', 'размьютить-в-сети', 'размьют'], description='Снять с пользователя мьют!')
    async def unmute(self, ctx: Context, member: Member):
        member.unmute_web()
        await ctx.send(member.mention + ' Полностью размьючен!')
