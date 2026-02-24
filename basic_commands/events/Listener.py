from ..library import Cog, Message, con, deps, Row, Webhook

class Listener(Cog):
    def give_fetch(self, channel_id: int) -> dict | None:
        connect = con(deps.DATABASE_MAIN_PATH)
        connect.row_factory = Row

        cursor = connect.cursor()

        cursor.execute("""
                       SELECT *
                       FROM shares
                       """)
        
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
        
        urls = fetch.get('webhooks_url', '').split(';')
        
        if not urls:
            return

        webhooks = [Webhook.from_url(url, session=deps.global_http) for url in urls if url]

        messages = []
        for webhook in webhooks:
            if webhook.channel_id != message.channel.id:
                messages.append((await webhook.send(
                    content=message.content,
                    username=message.author.display_name, 
                    avatar_url=message.author.display_avatar.url,
                    wait=True)).id)
        messages = ';'.join(messages)

        connect = con(deps.DATABASE_MAIN_PATH)
        cursor = connect.cursor()

        cursor.execute("""
                       INSERT INTO messages
                       (?, ?)
                       """, (message.id, messages))
        connect.commit()
        connect.close()

    @Cog.listener()
    async def on_message_edit(self, before: Message, after: Message):
        if before.author.bot:
            return

        connect = con(deps.DATABASE_MAIN_PATH)
        connect.row_factory = Row

        cursor = connect.cursor()

        cursor.execute("""
                       SELECT *
                       FROM messages
                       WHERE original = ?
                       """, (before.id,))
        
        messages = cursor.fetchone()
        connect.close()

        fetch = self.give_fetch(before.channel.id)

        if not messages or not fetch:
            return

        urls = [
            Webhook.from_url(url, session=deps.global_http) 
            for url in dict(fetch).get('webhooks_url', '').split(';') 
            if url
            ]

        for url in urls:
            try:
                await url.edit_message(message_id=int(dict(fetch).get('message_id')), content=after.content)
            except Exception as e:
                print(e)