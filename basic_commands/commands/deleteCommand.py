from ..library import hybrid_command, Context, con, deps, Webhook, logging

class DeleteCommand:
    @hybrid_command(name='delete-message', aliases=['delete_message', 'delmes', 'del-mes', 'del_mes', 'delete', 'message-delete', 'message_delete', 'удалить'])
    async def delete_message(self, ctx: Context):
        
        if not ctx.message.reference:
            await ctx.reply('Чтоб вызвать эту команду нужно ответить (forward/reply/reference) на чье-то сообщение!', ephemeral=True)
            return
        
        replied_message = await ctx.channel.fetch_message(ctx.message.reference.message_id)

        if (
            ctx.message.author != replied_message.author and 
            not (
                    (await ctx.author.is_m_transguild()) 
                    or 
                    (await ctx.author.is_a_transguild())
                )
            ):
            await ctx.reply('У вас нет права вызывать эту команду по отношению к кому-то кроме себя!')
            return
        try:
            with deps.main_db as connect:
                cursor = connect.cursor()

                cursor.execute(f"""
                            SELECT *
                            FROM messages
                            WHERE anothers LIKE '%{replied_message.id},%'
                            OR original LIKE '%{replied_message.id},%'
                            """)
                fetches = cursor.fetchall()
                cursor.close()
        except Exception as e:
            logging.error(f'Ошибка в delete_message: {e}')
            return
        
        for fetch in fetches:
            anothers = fetch['anothers'].split(';')
            for i in anothers:
                message_id, url = i.split(',')[0], i.split(',')[1]
                try:
                    webhook = Webhook.from_url(url, session=deps.second_http)
                    await webhook.delete_message(int(message_id))
                except:
                    continue
        
        await ctx.reply('Не забудь удалить оригинальное сообщение! Все остальные уже были удалены в сети межсервера!', delete_after=3)

    @hybrid_command(name='delete_history', aliases=['delete-history', 'del-history', 'del_history', 'history-delete', 'history_delete', 'удалить-историю'])
    async def delete_history(self, ctx: Context):
        if not (
            (await ctx.author.is_m_transguild()) 
            or 
            (await ctx.author.is_a_transguild())
        ):
            await ctx.reply('У вас нет права вызывать эту команду!')
            return
        
        try:
            with deps.main_db as connect:
                cursor = connect.cursor()

                cursor.execute("""
                            DELETE FROM messages
                            """)
                connect.commit()

                cursor.execute("""
                               SELECT COUNT(*) 
                               FROM messages
                               """)
                fetch = cursor.fetchone()[0]

                cursor.close()

                await ctx.send(f'Вся история сообщений удалена! Общее количество удаленых сообщений из базы данных равна {fetch}')
        except Exception as e:
            logging.error(f'Ошибка в delete_history: {e}')
            return