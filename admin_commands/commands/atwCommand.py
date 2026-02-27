from ..library import hybrid_command, Context, deps, describe, transguild_admin, Interaction, View, Button, con, Embed
from ..modals import AtwModal

class AddCommand:
    @hybrid_command(
        name='add-to-web',
        description='Присоединить текстовый канал к глобальной сети межсервера',
        aliases=['atw']
    )
    @describe(option="Опция команды", name='Название межсерверной сети')
    async def add_to_web(self, ctx: Context, option: str | None = None, name: str | None = None):
        """Опциональный параметр `option` принимает значения add/create/remove/delete.
        Если `option` не указан, выводится документация. Название сети требуется для create/delete/add/remove.
        """

        # базовая проверка прав
        if not await ctx.author.is_a_transguild():
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
        if option == 'add':
            if not name:
                await ctx.send('Укажите название межсерверной сети', ephemeral=True)
                return
            modal = AtwModal(name)
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
            button = Button(label='Нажми на меня')
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
            # TODO: реализовать удаление канала из сети
            await ctx.send('Опция remove пока не реализована', ephemeral=True)

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
        else:
            await ctx.send('Неизвестная опция, используйте add/create/remove/delete', ephemeral=True)