from ..library import con, deps, hybrid_command, Context, Row, Embed

class TransguildsCommand:
    @hybrid_command(name='transguilds', aliases=['transgs', 'transes'])
    async def transguilds(self, ctx: Context):
        connect = con(deps.DATABASE_MAIN_PATH)
        connect.row_factory = Row
        cursor = connect.cursor()

        cursor.execute("""
                       SELECT *
                       from shares
                       """)
        fetches = cursor.fetchall()
        connect.close()

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

