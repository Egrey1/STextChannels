from ..library import hybrid_command, Context, Interaction, View, Button, ButtonStyle, has_permissions, deps, SelectOption, logging
from ..modals import ItemsModal, EditItemModal

class ItemsCommands:
    @hybrid_command(name='create_item', aliases=['item-create', 'item_create', 'itemcreate', 'create-item', 'createitem', 'создать-предмет', "создать_предмет", "создатьпредмет"])
    @has_permissions(administrator=True)
    async def create_item(self, ctx: Context):
        if ctx.interaction:
            modal = ItemsModal(ctx.guild.id)
            await ctx.interaction.response.send_modal(modal)
            return
        
        async def callback(interaction: Interaction):
            if interaction.user.id != ctx.author.id:
                await interaction.response.send_message('Вы не имеете права исопльзовать чужую кнопку!', ephemeral=True)
                return
            modal = ItemsModal(ctx.guild.id)
            await interaction.response.send_modal(modal)
        
        view = View()
        button = Button(label='👆', style=ButtonStyle.green)

        button.callback = callback
        view.add_item(button)

        await ctx.send('Нажмите на кнопку для продолжения!', view=view)

    @hybrid_command(name='edit_item', aliases=['edit-item', 'edititem', 'itemedit', 'item-edit', 'item_edit'])
    @has_permissions(administrator=True)
    async def edit_item(self, ctx: Context):
        items = deps.GuildShopItems(ctx.guild.id).items
        
        async def callback(interaction: Interaction):
            if interaction.user.id != ctx.author.id:
                await interaction.response.send_message("Вы не можете пользоваться чужим выпадающим списком", ephemeral=True)
                return
            modal = EditItemModal(int(interaction.data['values'][0]), ctx.guild.id)
            await interaction.response.send_modal(modal)
        
        options = [SelectOption(label=item.name, value=item.id) for item in items]

        view = deps.ItemsView(options)
        view.select_callback = callback

        await ctx.send('Выберите предмет для изменения', view=view)

    @hybrid_command(name='delete_item', aliases=['delete-item', 'deleteitem', 'itemdelete', 'item-delete', 'item_delete'])
    @has_permissions(administrator=True)
    async def delete_item(self, ctx: Context):
        items = deps.GuildShopItems(ctx.guild.id).items
        
        async def callback(interaction: Interaction):
            if interaction.user.id != ctx.author.id:
                await interaction.response.send_message("Вы не можете пользоваться чужим выпадающим списком", ephemeral=True)
                return
            id_ = interaction.data['values'][0]
            try:
                with deps.economic_db as connect:
                    cursor = connect.cursor()
                    
                    cursor.execute("""
                                   DELETE FROM shop
                                   WHERE item_id = ?
                                   """, (id_, ))
                    connect.commit()
                    cursor.close()

                    await interaction.response.send_message("Предмет успешно удален с вашего магазина")
            except Exception as e:
                logging.error(f'Ошибка в edit_item.callback: {e}')
        
        options = [SelectOption(label=item.name, value=item.id) for item in items] 

        view = deps.ItemsView(options)
        view.select_callback = callback

        await ctx.send('Выберите предмет для удаления', view=view)