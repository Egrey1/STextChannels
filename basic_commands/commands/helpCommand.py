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
            value='Создает/удаляет межсерверную сеть или добавляет канал в уже существующую. Во время использования рекомендуется не создавать слишком много вебхуков. Хватит и одного для всех задач. Команда доступна только для администраторов межсервера. Исключение опция remove, она доступна еще и для администраторов серверов'
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
        embed.add_field(
            name='$$mute ^reply | @',
            value='Мьютит участника в определенном канале, сети или вовсе везде. Чтобы не передавать параметр @пользователя можно просто ответить на его сообщение (необязательно оригинальное). В модальном окне нужно передать время мьюта. Команда доступна только модераторам межсервера',
            inline=False
        )
        embed.add_field(
            name='$$unmute ^reply | @',
            value='Снимает с @пользователя все мьюты. Команда доступна только модераторам межсервера',
            inline=False
        )
        embed.add_field(
            name='$$add-money <число> [@]',
            value='Прибавляет <число> кредитов @пользователю или серверу (если второй параметр пуст). Вызвать ее может только администратор экономики',
            inline=False
        )
        embed.add_field(
            name='$$set-money <число> [@]',
            value='Устанавливает <число> кредитов @пользователю или серверу (если второй параметр пуст). Вызвать ее может только администратор экономики',
            inline=False
        )
        embed.add_field(
            name='$$remove-moeny <число> [@]',
            value='Забирает <число> кредитов у @пользователя или сервера',
            inline=False
        )
        embed.add_field(
            name='$$create-item',
            value='Создает новый предмет для покупки в локальном магазине сервера. Команда доступна только администраторам',
            inline=False
        )
        embed.add_field(
            name='$$edit-item',
            value='Редактирует существующий предмет в локальном магазине сервера. Команда доступна только администраторам',
            inline=False
        )
        embed.add_field(
            name='$$delete-item',
            value='Удаляет существующий предмет в локальном магазине сервера. Команда доступна только администраторам',
            inline=False
        )
        embed.add_field(
            name='$$shop',
            value='Просмотр магазина сервера, откуда была вызвана команда',
            inline=False
        )
        embed.add_field(
            name='$$shops',
            value='Просмотр всех доступных магазинов по серверам',
            inline=False
        )
        embed.add_field(
            name='$$guild-partner',
            value='Просмотр информации о сервере как о сервере-партнере цитадели',
            inline=False
        )
        embed.add_field(
            name='$$add_guild-partner',
            value='Добавление сервера, где была вызвана команда, в состав серверов-партнеров цитадели. Команда доступна только для ОПСК',
            inline=False
        )
        embed.add_field(
            name='$$delete_guild-partner [число]',
            value='Удаление сервера партнера, по id=[число] или по месту где была вызвана команда, из состава Цитадели. Команда доступна только для ОПСК',
            inline=False
        )
        embed.set_footer(
            text='Сделано с любовью Егреем',
            icon_url='https://images-ext-1.discordapp.net/external/N1nHsFN90HGc4BY2qTCYZ9Ip-vJ-UrfMUU5yfVc3NSg/https/cdn.discordapp.com/avatars/820595582027956247/ce03d2bc7e2cd21fe0551d02828aa2ff.png?format=webp&quality=lossless&width=141&height=141'
        )

        await ctx.send(embed=embed)
        