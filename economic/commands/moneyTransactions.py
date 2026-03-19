from ..library import hybrid_command, describe, Context, Member, Guild, logging

class AddMoneyCommand:
    @hybrid_command(
            name='add-money', 
            aliases=['add_money', 'money_add', 'money-add', 'addmoney', 'moneyadd'], 
            description='Дать денег серверу или пользователю'
            )
    @describe(value='Количество добавляемых', member='Если пусто выбирается сервер где была вызвана команда')
    async def add_money(self, ctx: Context, value: int, member: Member = None):
        if not (await ctx.author.is_a_shop()):
            await ctx.send('Вы не имеете права использовать эту команду!', ephemeral=True)
            return
        if (member is None) and (ctx.message.reference is None):
            member = ctx.guild
        elif member is None:
            try:
                member = ctx.guild.get_member(ctx.message.reference.resolved.author)
            except Exception as e:
                logging.error(f'Ошибка в add_money: {e}')
                await ctx.send('Что-то пошло не так!', ephemeral=True)
                return
        elif value < 1:
            await ctx.send('Нельзя вводить отрицательное число или 0!', ephemeral=True)
            return
        
        await member.add_money(value, ctx.author)
        await ctx.send('Все прошло успешно!')
    
    @hybrid_command(
            name='remove-money', 
            aliases=['remove_money', 'money_remove', 'money-remove', 'removemoney', 'moneyremove'], 
            description='Удалить деньги у сервера или пользователя'
    )
    @describe(value='Количество отнимаемых денег', member='Если пусто выбирается сервер где была вызвана команда')
    async def remove_money(self, ctx: Context, value: int, member: Member = None):
        if not (await ctx.author.is_a_shop()):
            await ctx.send('Вы не имеете права использовать эту команду!', ephemeral=True)
            return
        if (member is None) and (ctx.message.reference is None):
            member = ctx.guild
        elif member is None:
            try:
                member = ctx.guild.get_member(ctx.message.reference.resolved.author)
            except Exception as e:
                logging.error(f'Ошибка в add_money: {e}')
                await ctx.send('Что-то пошло не так!', ephemeral=True)
                return
        elif value < 1:
            await ctx.send('Нельзя вводить отрицательное число или 0!', ephemeral=True)
            return
        
        await member.add_money(-value, ctx.author)
        await ctx.send('Все прошло успешно!')


    @hybrid_command(
            name='balance',
            aliases=['bal', 'баланс', 'бал'],
            description='Посмотреть баланс сервера или пользователя'
    )
    @describe(member='Если пусто, то просмореть баланс сервера')
    async def balance(self, ctx: Context, member: Member = None):
        await ctx.send(
            f'Баланс сервера `{ctx.guild.name}` равен {(ctx.guild.get_money()):.2f}' 
            if member is None else 
            f'Баланс пользователя {member.mention} равен {(member.get_money()):.2f}'
            )
    

    @hybrid_command(
            name='set_money',
            description='Установить новый баланс пользователю или серверу'
    )
    @describe(value='Новое значение баланса', member='Пользователь или сервер (если пусто)')
    async def set_money(self, ctx: Context, value: int, member: Member = None):
        if not (await ctx.author.is_a_shop()):
            await ctx.send('Вы не имеете права использовать эту команду!', ephemeral=True)
            return
        
        member = member if member is not None else ctx.guild

        await member.set_money(value, ctx.author)

        await ctx.send(f'Операция прошла успешно! У {member.name} теперь новый баланс!')