from ..library import Cog, Message, con, deps, Row, Webhook, AllowedMentions, List, AuditLogAction
import logging

class Listener(Cog):
    def give_fetch(self, channel_id: int) -> List[dict] | None:
        connect = con(deps.DATABASE_MAIN_PATH)
        connect.row_factory = Row
        cursor = connect.cursor()
        cursor.execute(
            """
            SELECT *
            FROM shares
            """
        )
        fetches = cursor.fetchall()
        connect.close()

        result: List[dict] = []

        for fetch in fetches:
            fetch = dict(fetch)
            channels = fetch.get('channels', '').split(';')
            for channel in channels:
                if str(channel_id) in channel.split(','):
                    result.append(fetch)

        return result if result else None

    @Cog.listener()
    async def on_message(self, message: Message):
        if (message.author.bot) or (message.content.startswith(deps.PREFIX)):
            return

        fetches = self.give_fetch(message.channel.id)
        if not fetches:
            return

        # если сообщение является ответом на предыдущий, попытаться получить URL
        header = ""
        if message.reference and message.reference.message_id:
            ref_id = message.reference.message_id
            with con(deps.DATABASE_MAIN_PATH) as connect:
                cursor = connect.cursor()
                cursor.execute(
                    "SELECT anothers FROM messages WHERE anothers LIKE ?",
                    (f"{ref_id},%",),
                )
                row = cursor.fetchone()
            if row:
                anothers = row['anothers'] if isinstance(row, Row) else row[0]
                for entry in str(anothers).split(';'):
                    parts = entry.split(',')
                    if parts[0] == str(ref_id) and len(parts) >= 3:
                        header = f"Отвечая на сообщение {parts[2]}"
                        break

        for fetch in fetches:
            # deps.global_http
            urls = [
                u.split(',')[1] 
                for u in dict(fetch).get('channels', '').split(';') 
                if u and u.split(',')[0] != str(message.channel.id)
                ]
            
            if not urls:
                return
            
            replied = message.reference

            

            # results = await asyncio.gather(*coros, return_exceptions=True)
            webhooks = []
            for url in urls:
                try:
                    w = Webhook.from_url(url, session=deps.global_http)
                    webhooks.append(w)
                except:
                    continue

            sent_ids = []
            for webhook in webhooks:
                try:
                    content = message.content
                    if header:
                        content = content + "\n\n" + header
                    sent = await webhook.send(
                        content=content,
                        username=message.author.global_name,
                        avatar_url=message.author.display_avatar.url,
                        wait=True,
                        allowed_mentions=AllowedMentions.none()
                    )
                    if sent.channel.id == message.channel.id:
                        await sent.delete()
                    else:
                        sent_ids.append(str(sent.id) + ',' + (webhook.url) + ',' + (sent.jump_url))
                except Exception:
                    logging.exception('Failed to send message via webhook')

            forwarded = ';'.join(sent_ids)
            if forwarded:
                connect = con(deps.DATABASE_MAIN_PATH)
                cursor = connect.cursor()
                cursor.execute(
                    """
                    INSERT INTO messages (original, anothers)
                    VALUES (?, ?)
                    """,
                    (message.id, forwarded),
                )
                connect.commit()
                connect.close()

    @Cog.listener()
    async def on_message_edit(self, before: Message, after: Message):
        if before.author.bot:
            return

        connect = con(deps.DATABASE_MAIN_PATH)
        connect.row_factory = Row
        cursor = connect.cursor()
        cursor.execute(
            """
            SELECT anothers
            FROM messages
            WHERE original = ?
            """,
            (before.id,),
        )
        row = cursor.fetchone()
        connect.close()

        if not row:
            return

        forwarded = row['anothers'] if isinstance(row, Row) else row[0]
        forwarded_ids = [s for s in str(forwarded).split(';') if s]
        if not forwarded_ids:
            return

        fetches = self.give_fetch(before.channel.id)
        if not fetches:
            return

        for fetch in fetches:
            urls = [
                u.split(',')[1]
                for u in dict(fetch).get('channels', '').split(';') 
                if u
                ]
            if not urls:
                return

            for forw in forwarded_ids:
                msg_id, url = tuple(forw.split(','))
                webhook = Webhook.from_url(url, session=deps.global_http)
                try:
                    await webhook.edit_message(message_id=int(msg_id), content=after.content)
                except Exception:
                    logging.exception('Failed to edit forwarded message')