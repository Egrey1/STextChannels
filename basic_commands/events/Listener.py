from ..library import Cog, Message, deps, Reaction, Member, Webhook, TextChannel, dt, DMChannel
from ..library import on_sended, on_edited, on_sended_replaied
import asyncio
import logging

class Listener(Cog):
    # хранение состояния печати: источник -> {user_id: last_timestamp}
    _typing_state: dict[int, dict[int, float]] = {}
    # задачи, поддерживающие индикаторы печати для канала
    _typing_tasks: dict[int, asyncio.Task] = {}

    async def _typing_loop(self, source_channel: TextChannel):
        while True:
            now = asyncio.get_running_loop().time()
            user_times = self._typing_state.get(source_channel.id, {})

            # очищаем устаревшую активность (например, 8 секунд нет on_typing)
            stale = [uid for uid, ts in user_times.items() if now - ts > 8]
            for uid in stale:
                user_times.pop(uid, None)

            if not user_times:
                break

            webs = source_channel.get_all_webs()
            for web in webs:
                for channel_id in web.groups:
                    try:
                        if channel_id['channel_id'] != source_channel.id:
                            dest = await deps.bot.fetch_channel(channel_id['channel_id'])
                            await dest.typing()
                    except Exception as e:
                        logging.warning(f"Ошибка trigger_typing для канала {channel_id}: {e}")
                        continue

            await asyncio.sleep(5)

        self._typing_tasks.pop(source_channel.id, None)
        self._typing_state.pop(source_channel.id, None)

    @Cog.listener()
    async def on_message(self, message: Message):
        if (
                (isinstance(message.channel, DMChannel)) or
                (message.webhook_id) or 
                (message.content.startswith(deps.PREFIX)) or 
                (
                    (
                        ('https://' in message.content) or 
                        ('http://'  in message.content)
                    ) and not 
                    any(exception in message.content for exception in deps.automod_exceptions)
                )
            ):
            if (not message.author.bot) and (message.channel.get_all_webs()):
                logging.info(f'Сообщение заблокировано на сервере {message.guild.name[:25]}')
            elif not (message.channel.get_all_webs()):
                return
            else:
                logging.info("Сообщение заблокировано")
            return
        
        if message.reference:
            try:
                await on_sended_replaied(message)
            except TypeError:
                return
            except Exception:
                try:
                    await on_sended(message)
                except TypeError:
                    return
            return
        

        try:
            await on_sended(message)
        except TypeError:
            return


    @Cog.listener()
    async def on_message_edit(self, before: Message, after: Message):
        if before.author.bot:
            return

        await on_edited(before, after)

    @Cog.listener()
    async def on_reaction_add(self, reaction: Reaction, user: Member):
        if user.id == deps.bot.user.id:
            return
        webmes = deps.WebhookMessagesSended(message_id=reaction.message.id)
        
        for another in (webmes.anothers + [webmes.original]):
            try:
                message = await (await deps.bot.fetch_channel(int(another.channel_id))).fetch_message(int(another.message_id))
                if message.id != reaction.message.id:
                    await message.add_reaction(reaction.emoji)
            except:
                continue
    
    @Cog.listener()
    async def on_reaction_remove(self, reaction: Reaction, user: Member):
        if user.id == deps.bot.user.id:
            return
        
        if len(reaction.message.reactions) <= 1:
            webmes = deps.WebhookMessagesSended(message_id=reaction.message.id)
            
            for another in webmes.anothers:
                try:
                    message = await (await deps.bot.fetch_channel(int(another.channel_id))).fetch_message(int(another.message_id))
                    await message.remove_reaction(reaction, deps.bot.user)
                except:
                    continue

    @Cog.listener()
    async def on_message_delete(self, message: Message):
        if message.webhook_id:
            return
        
        await deps.WebhookMessagesSended(message_id=message.id).delete()

    # Сейчас проверять будем, когда пользователь что-то печатает, оставим без реализации, пока что
    @Cog.listener()
    async def on_typing(self, channel: TextChannel, user: Member, when: dt.datetime):
        # игнорируем ботов (включая самого себя) и пустые веб-подключения
        if user.bot or user.id == deps.bot.user.id:
            return

        webs = channel.get_all_webs()
        if not webs:
            return

        # отметим активность печати участника в исходном канале
        now = asyncio.get_running_loop().time()
        source_id = channel.id

        users = self._typing_state.setdefault(source_id, {})
        users[user.id] = now

        # если цикл уже запущен, продолжает работу, иначе стартуем
        if source_id not in self._typing_tasks or self._typing_tasks[source_id].done():
            logging.debug(f"Start typing loop for channel {source_id} due to user {user.id}")
            self._typing_tasks[source_id] = asyncio.create_task(self._typing_loop(channel))


