from ..library import hybrid_command, Context, deps, SelectOption, View, Select, Interaction, logging, List

class ShopCommand:
    @hybrid_command(name='shop', aliases=['магазин', 'магаз', 'buy', 'купить'])
    async def shop(self, ctx: Context):
        shop = deps.Shop(ctx)
        await shop.send()
    
    @hybrid_command(name='shops', aliases=['магазины', 'магазы'])
    async def shops(self, ctx: Context):
        try:
            with deps.economic_db as connect:
                cursor = connect.cursor()
                cursor.execute("""
                               SELECT DISTINCT guild_id
                               FROM shop
                               """)
                fetches = cursor.fetchall()
                cursor.close()

                options: List[SelectOption] = []
                my_set = {}
                for guild_ids in fetches:
                    guild_id = int(guild_ids['guild_id'])

                    try:
                        guild = await deps.bot.fetch_guild(guild_id)
                    except:
                        continue

                    
                    options.append(
                        SelectOption(
                            label=guild.name[:100],
                            value=guild.id
                        )
                    )
                
                if not options:
                    await ctx.send('Магазинов пока нет!', ephemeral=True)
                    return
                
                view = View()
                select = Select(placeholder='Сервера', options=options)

                async def callback(interaction: Interaction):
                    shop = deps.Shop(ctx, int(interaction.data['values'][0]))
                    await shop.send()
                    await interaction.response.send_message('Отправлено!')
                
                select.callback = callback
                view.add_item(select)

                await ctx.send('Выберите сервер!', view=view)
        except Exception as e:
            logging.error(f'Ошибка в shops: {e}')