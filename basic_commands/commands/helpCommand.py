from ..library import hybrid_command, Embed, deps, Context

class HelpCommand:
    @hybrid_command(name='help')
    async def help(self, ctx: Context):
        temp = '`,`'.join(deps.PREFIX)
        embed = Embed(
            title='Административная справка по пользованию межсервером',
            description=f'Все преффиксы: `' + temp + '`'
        )

        embed.add_field(
            name='$$add-to-web (сокр. atw)',
            value='Создает/удаляет межсерверную сеть или добавляет канал в уже существующую. Во время использования рекомендуется не создавать слишком много вебхуков. Хватит и одного для всех задач'
        )
        embed.add_field(
            name='$$delete',
            value='Удаляет сообщение отовсюду кроме оригинального. Применить эту команду может кто угодно если он является автором удаляемого сообщения или модератором межсерверной сети\nЧтоб ее использовать нужно ответить на удаляемое сообщение',
            inline=False
        )
        embed.add_field(
            name='$$help',
            value='Выводит данную информацию',
            inline=False
        )
        embed.add_field(
            name='$$transguild (сокр. transg)',
            value='Выводит все подключенные межсерверные сети в канале, где была вызвана команда',
            inline=False
        )
        embed.add_field(
            name='$$transguilds (сокр. transgs)',
            value='Выводит все межсерверные сети',
            inline=False
        )
        embed.set_footer(
            text='Сделано с любовью Егреем',
            icon_url='https://images-ext-1.discordapp.net/external/N1nHsFN90HGc4BY2qTCYZ9Ip-vJ-UrfMUU5yfVc3NSg/https/cdn.discordapp.com/avatars/820595582027956247/ce03d2bc7e2cd21fe0551d02828aa2ff.png?format=webp&quality=lossless&width=141&height=141'
        )

        await ctx.send(embed=embed)
        