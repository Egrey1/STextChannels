from ..library import hybrid_command, Context, deps, describe, transguild_admin, Interaction, View, Button, con, Embed, logging, ButtonStyle
from ..modals import AtwAddModal, AtwEditModal
from discord.abc import GuildChannel

class AddCommand:
    @hybrid_command(
        name='add-to-web',
        description='Присоединить текстовый канал к глобальной сети межсервера',
        aliases=['atw', 'ксети', "к-сети", "к_сети"]
    )
    @describe(option="Опция команды", name='Название межсерверной сети')
    async def add_to_web(self, ctx: Context, option: str | None = None, name: str | None = None):
        """Опциональный параметр `option` принимает значения add/create/remove/delete.
        Если `option` не указан, выводится документация. Название сети требуется для create/delete/add.
        """
        
        # базовая проверка прав
        if (
            (not await ctx.author.is_a_transguild()) and not
            (ctx.permissions.administrator and option == 'remove')
            ):
            await ctx.send('У вас нет прав на использование этой команды')
            return

        # если опция не задана — показать справку
        if not option:
            embed = Embed(
                title='Документация к команде add-to-web',
                description='У этой команды есть опции'
            )
            embed.add_field(name='add', value='Добавить канал к сети межсервера', inline=False)
            embed.add_field(name='create', value='Создать сеть межсервера', inline=False)
            embed.add_field(name='remove', value='Удалить канал из сети межсервера (пока недоступно)', inline=False)
            embed.add_field(name='delete', value='Удалить сеть межсервера', inline=False)
            embed.set_footer(text='Значение по умолчанию: add')
            await ctx.send(embed=embed, ephemeral=True)
            return

        # стандартизируем название опции
        option = option.lower()
        if (option == 'add') or ((name == None) and (option != 'remove')):
            name = option if name is None else name
            if not name:
                await ctx.send('Укажите название межсерверной сети', ephemeral=True)
                return
            
            modal = AtwAddModal(name, ctx.bot_permissions.manage_webhooks)
            if ctx.interaction:
                await ctx.interaction.response.send_modal(modal)
                return

            async def if_is_not_interaction(interaction: Interaction):
                if interaction.user.is_a_transguild:
                    await interaction.response.send_modal(modal)
                else:
                    await interaction.response.send_message(
                        'Вы не имеете права вызывать модальное окно администратора межсервера',
                        ephemeral=True,
                    )

            view = View()
            button = Button(label='👆', style=ButtonStyle.green)
            button.callback = if_is_not_interaction
            view.add_item(button)
            await ctx.send('Нажми на кнопку чтобы открыть модальное окно', view=view)

        elif option == 'create':
            if not name:
                await ctx.send('Укажите название создаваемой сети', ephemeral=True)
                return
            try:
                with con(deps.DATABASE_MAIN_PATH) as connect:
                    cursor = connect.cursor()
                    cursor.execute(
                        "INSERT INTO shares (name) VALUES (?)",
                        (name,),
                    )
                    connect.commit()
                await ctx.send('Новый межсервер добавлен!')
            except Exception:
                await ctx.send(
                    'Скорее всего это название межсервера уже используется, возьмите другое или обратитесь к разработчику!',
                    ephemeral=True,
                )

        elif option == 'remove':
            try:
                with deps.main_db as connect:
                    cursor = connect.cursor()

                    cursor.execute("""
                                   SELECT *
                                   FROM shares
                                   WHERE channels LIKE ?
                                   """, (f'%{ctx.channel.id},%', ))
                    fetches = cursor.fetchall()
                    names = []

                    if not fetches:
                        await ctx.send('Этот канал не состоял ни в одном межсервере!', ephemeral=True)
                        return

                    for fetch in fetches:
                        names.append(fetch['name'])
                        ifirst = fetch['channels'].find(str(ctx.channel.id))
                        rfirst = fetch['channels'].find(';', ifirst)
                        rfirst = rfirst if rfirst != -1 else len(fetch['channels']) - 1
                        channels_to_delete = fetch['channels'][ifirst:rfirst + 1]
                        new_channels = fetch['channels'].replace(channels_to_delete, '').replace(',,', ',')
                        new_channels = new_channels[:-1] if new_channels[-1] == ';' else new_channels
                        cursor.execute("""
                                       UPDATE shares
                                       SET channels = ?
                                       WHERE name = ?
                                       """, (new_channels, fetch['name']))
                    cursor.close()

                    await ctx.send('Ваш канал успешно удален из всех межсерверов! Вот их список: ' + ', '.join(names), ephemeral=True)
            except Exception as e:
                logging.error(f'Ошибка в remove_to_web: {e}')

        elif option == 'delete':
            if not name:
                await ctx.send('Укажите название удаляемой сети', ephemeral=True)
                return
            try:
                with con(deps.DATABASE_MAIN_PATH) as connect:
                    cursor = connect.cursor()
                    cursor.execute("""
                        DELETE 
                        FROM shares 
                        WHERE name = ?
                        """, (name,),
                    )
                    connect.commit()
                await ctx.send(f'Межсервер {name} успешно удален из базы')
            except Exception:
                await ctx.send('Что-то пошло не так!')
        
        elif option == 'edit':
            if not name:
                await ctx.send('Укажите название редактируемой сети')
            try:
                modal = AtwEditModal(name)
            except ValueError:
                await ctx.send('Неверно указано название межсерверной сети')
                return
            
            if ctx.interaction:
                await ctx.interaction.response.send_modal(modal)
                return

            async def if_is_not_interaction(interaction: Interaction):
                if interaction.user.is_a_transguild:
                    await interaction.response.send_modal(modal)
                else:
                    await interaction.response.send_message(
                        'Вы не имеете права вызывать модальное окно администратора межсервера',
                        ephemeral=True,
                    )

            view = View()
            button = Button(label='👆', style=ButtonStyle.green)
            button.callback = if_is_not_interaction
            view.add_item(button)
            await ctx.send('Нажми на кнопку чтобы открыть модальное окно', view=view)
        
        else:
            await ctx.send('Неизвестная опция, используйте add/create/remove/delete', ephemeral=True)
