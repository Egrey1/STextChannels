from ..library import hybrid_command, deps, con, Context, Row, Embed

class TransguildCommand:
    @hybrid_command(
        name='transguild',
        aliases=['transg', 'trans', 'межсервер', "сеть"]
    )
    async def transguild(self, ctx: Context):
        connect = con(deps.DATABASE_MAIN_PATH)
        connect.row_factory = Row
        cursor = connect.cursor()

        cursor.execute(f"""
                        SELECT *
                        from shares
                        WHERE channels LIKE '%{ctx.channel.id},%'
                        """)
        fetches = cursor.fetchall()
        connect.close()

        embed = Embed(
            title='Подключенные сети межсервера в этом канале',
            description=f'Общее количество {len(fetches)}' if len(fetches) != 0 else 'Подключенных сетей нет'
        )

        for fetch in fetches:
            embed.add_field(
                name=fetch['name'],
                value=fetch['description'] if fetch['description'] else 'Описание отсутствует',
                inline=False
            )
        await ctx.send(embed=embed, ephemeral=True)