from ..library import con, deps, hybrid_command, Context, Row, Embed

class TransguildsCommand:
    @hybrid_command(name='transguilds', aliases=['transgs', 'transes', 'межсервера', "сети"])
    async def transguilds(self, ctx: Context):
        try:
            with deps.main_db as connect:
                cursor = connect.cursor()

                cursor.execute("""
                            SELECT *
                            from shares
                            """)
                fetches = cursor.fetchall()
                cursor.close()

                embed = Embed(
                    title='Список доступных межсерверов',
                    description=f'Общее количество: {len(fetches)}'
                )

                for fetch in fetches:
                    embed.add_field(
                        name= fetch['name'],
                        value= fetch['description'] if fetch['description'] else 'Описание отсутствует',
                        inline=False
                    )
                await ctx.send(embed=embed, ephemeral=True)
        except Exception as e:
            await ctx.send(f'Ошибка: {e}', ephemeral=True)



