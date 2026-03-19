from ..library import hybrid_command, Context, Embed, View, Button, Interaction, ButtonStyle, deps, logging
from ..modals import AddGPModal

class GuildPartners:
    @hybrid_command(name='guild-partner', aliases=['gp', 'guild_partner', 'guildpartner', 'сервер-партнер', "сервер_партнер", "серверпартнер", "сп"])
    async def guild_partner(self, ctx: Context):
        guild_partner = await ctx.guild.guild_partner()
        if guild_partner is None:
            await ctx.send("Этот сервер не входит в состав Цитадели", ephemeral=True)
            return
        embed = Embed(title=guild_partner.partner_name, description=guild_partner.partner_description)
        embed.set_footer(text='Метки сервера: ' + ','.join(guild_partner.marks))
        await ctx.send(embed=embed, ephemeral=True)
    
    @hybrid_command(name='guild-partners', aliases=['gps', 'guild_partners', 'guildpartners', 'сервера-партнеры', "сервера_партнеры", "серверапартнеры", "сапы"])
    async def guild_partners(self, ctx: Context):
        """Оставлю реализацию на потом"""
    
    @hybrid_command(name='add_gp', aliases=['add_guild-partner', 'add_guild_partner', 'add_guildpartner', 'добавить_сп', "добавить_сервер-партнер", "добавить_сервер_партнер", "добавить_серверпартнер"])
    async def add_gp(self, ctx: Context):
        if not (await ctx.author.is_OPSK() or await ctx.author.is_citadel_leader()):
            await ctx.send('Вы не имеете права использовать эту команду', ephemeral=True)
            return
        
        if ctx.interaction:
            modal = AddGPModal(ctx.guild.id)
            ctx.interaction.response.send_modal(modal)
            return
        
        async def bt_callback(interaction: Interaction):
            if interaction.user.id != ctx.author.id:
                await interaction.response.send_message('Вы не имеете права исопльзовать чужую кнопку!', ephemeral=True)
                return
            modal = AddGPModal(ctx.guild.id)
            await interaction.response.send_modal(modal)
        
        view = View()
        bt = Button(label='👆', style=ButtonStyle.green)

        bt.callback = bt_callback
        view.add_item(bt)

        await ctx.send('Для продолжения нажмите на кнопку', view=view)
    
    @hybrid_command(name='dgp', aliases=['delete_gp', 'delete_guild-partner', 'delete_guild_partner', 'delete_guildpartner', 'удалить_сп', "удалить_сервер-партнер", "удалить_сервер_партнер", "удалить_серверпартнер"])
    async def delete_gp(self, ctx: Context, id_: int | None = None):
        if not (await ctx.author.is_OPSK() or await ctx.author.is_citadel_leader()):
            await ctx.send('Вы не имеете права использовать эту команду', ephemeral=True)
            return
        
        async def bt_callback(interaction: Interaction):
            if not interaction.user.id == ctx.author.id:
                await interaction.response.send_message('Вы не имеете права исопльзовать чужую кнопку!', ephemeral=True)
                return
            
            id_ = id_ if id_ else ctx.guild.id
            try:
                with deps.main_db as connect:
                    cursor = connect.cursor()

                    cursor.execute("""
                                   DELETE FROM guild_partners
                                   WHERE id = ?
                                   """, (id_ ))
                    connect.commit()
                    cursor.close()
                await interaction.response.send_message('Сервер-партнер удален!', ephemeral=True)
            except Exception as e:
                await interaction.response.send_message('Произошла непредвиденная ошибка!')
                logging.error(f'Ошибка в dgp.callback: {e}')
        
        view = View()
        bt = Button(label='Да, я уверен')

        bt.callback = bt_callback
        view.add_item(bt)

        await ctx.send(f"Вы уверены что хотите удалить сервер с идентификатором {id_ if id_ else ctx.guild.id}?", view=view)
