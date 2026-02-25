from ..library import hybrid_command, Context, deps, describe, transguild_admin, Interaction, View, Button
from ..modals import AtwModal

class AddCommand:
    @hybrid_command(
        name='add-to-web',
        description='Присоединить текстовый канал к глобальной сети межсервера',
        aliases=['atw']
    )
    @describe(name='Название межсерверной сети')
    @transguild_admin()
    async def add_to_web(self, ctx: Context, name: str):
        modal = AtwModal(name)
        
        if ctx.interaction:
            await ctx.interaction.response.send_modal(modal)
            return

        async def if_is_not_interaction(interaction: Interaction):
            await interaction.response.send_modal(modal)
        
        view = View()

        button = Button(label='Нажми на меня')
        button.callback = if_is_not_interaction
        view.add_item(button)

        await ctx.send('Нажми на кнопку чтобы открыть модальное окно', view=view)