from ..library import Cog, Message, con, deps, Row, Webhook, AllowedMentions, List, AuditLogAction
from ..library import on_sended, on_edited, on_sended_replaied
import logging

class Listener(Cog):
    @Cog.listener()
    async def on_message(self, message: Message):
        if (
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
            else:
                logging.info("Сообщение заблокировано")
            return
        
        if message.reference:
            try:
                await on_sended_replaied(message)
            except TypeError:
                logging.info("Сообщение заблокировано")
            except Exception:
                try:
                    await on_sended(message)
                except TypeError:
                    logging.info("Сообщение заблокировано")
            return
        

        await on_sended(message)


    @Cog.listener()
    async def on_message_edit(self, before: Message, after: Message):
        if before.author.bot:
            return

        await on_edited(before, after)
