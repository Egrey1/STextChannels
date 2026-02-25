from ..library import Cog, Message, con, deps, Row, Webhook, AllowedMentions
import asyncio
import logging

logging.basicConfig(level=logging.INFO)


class Listener(Cog):
    def give_fetch(self, channel_id: int) -> dict | None:
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

        for fetch in fetches:
            fetch = dict(fetch)
            if str(channel_id) in fetch.get('text_channels', '').split(';'):
                return fetch

        return None

    @Cog.listener()
    async def on_message(self, message: Message):
        if message.author.bot:
            return

        fetch = self.give_fetch(message.channel.id)
        if not fetch:
            return

        urls = [u for u in dict(fetch).get('webhooks_url', '').split(';') if u]
        if not urls:
            return
        


        # results = await asyncio.gather(*coros, return_exceptions=True)
        webhooks = []
        for url in urls:
            try:
                w = Webhook.from_url(url, session=deps.global_http)
                if w.channel_id != message.channel.id:
                    webhooks.append(w)
            except:
                continue

        sent_ids = []
        for webhook in webhooks:
            if webhook.channel_id == message.channel.id:
                continue
            try:
                sent = await webhook.send(
                    content=message.content.replace('@', '`@`'),
                    username=message.author.display_name,
                    avatar_url=message.author.display_avatar.url,
                    wait=True,
                    allowed_mentions=AllowedMentions.none
                )
                if sent.channel.id == message.channel.id:
                    await sent.delete()
                else:
                    sent_ids.append(str(sent.id) + ',' + (webhook.url))
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

        fetch = self.give_fetch(before.channel.id)
        if not fetch:
            return

        urls = [u for u in dict(fetch).get('webhooks_url', '').split(';') if u]
        if not urls:
            return

        for forw in forwarded_ids:
            msg_id, url = tuple(forw.split(','))
            webhook = Webhook.from_url(url, session=deps.global_http)
            try:
                await webhook.edit_message(message_id=int(msg_id), content=after.content)
            except Exception:
                logging.exception('Failed to edit forwarded message')