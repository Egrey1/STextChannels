from .modules import Message, con, Row, deps, Webhook, logging, AllowedMentions, List

def give_fetch(channel_id: int) -> List[dict] | None:
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


async def on_sended(message: Message):
    fetches = give_fetch(message.channel.id)
    if not fetches:
        return

    for fetch in fetches:
        original = str(message.id) + ','
        urls = []
        
        for u in dict(fetch).get('channels', '').split(';'):
            if u.split(',')[0] == str(message.channel.id):
                original += u.split(',')[1] + ',' + message.jump_url
                continue
            urls.append(u.split(',')[1])
        
        if not urls:
            return
        


        # results = await asyncio.gather(*coros, return_exceptions=True)
        webhooks: List[Webhook] = []
        for url in urls:
            try:
                w = Webhook.from_url(url, session=deps.global_http)
                webhooks.append(w)
            except:
                continue

        sent_ids = []
        for webhook in webhooks:
            try:
                files = [await attachment.to_file() for attachment in message.attachments] if message.attachments else []

                sent = await webhook.send(
                    content=message.content,
                    username=message.author.global_name,
                    avatar_url=message.author.display_avatar.url,
                    wait=True,
                    files=files[:10],
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
                (original, forwarded),
            )
            connect.commit()
            connect.close()

async def on_sended_replaied(message: Message):
    replied = message.reference

    connect = con(deps.DATABASE_MAIN_PATH)
    connect.row_factory = Row
    cursor = connect.cursor()

    cursor.execute("""
                    SELECT *
                    FROM messages
                    WHERE original LIKE ?
                    OR anothers LIKE ?
                    """, (f"%{replied.message_id},%", f"%{replied.message_id},%"))
    fetches = cursor.fetchall()
    connect.close()

    if not fetches:
        return
    
    sent_ids = []

    for fetch in fetches:
        fetch = dict(fetch)
        s = fetch['original'] + (';' + fetch['anothers']) if fetch['anothers'] else ''
        for webmes in s.split(';'):
            mes_id, webhook_url, mes_url = webmes.split(',')[0], webmes.split(',')[1], webmes.split(',')[2]

            files = [await attachment.to_file() for attachment in message.attachments] if message.attachments else []
            files += [await sticker.to_file() for sticker in message.stickers] if message.stickers else []

            webhook: Webhook = Webhook.from_url(webhook_url, session=deps.global_http)
            
            sent = await webhook.send(
                    content=f'> -# Ответ на {mes_url}\n\n' + message.content,
                    username=message.author.global_name,
                    avatar_url=message.author.display_avatar.url,
                    files=files[:10],
                    wait=True,
                    allowed_mentions=AllowedMentions.none()
                )

            if sent.channel.id == message.channel.id:
                await sent.delete()
            else:
                sent_ids.append(str(sent.id) + ',' + (webhook.url) + ',' + (sent.jump_url))

    forwarded = ';'.join(sent_ids) if sent_ids else None
    if forwarded:
        connect = con(deps.DATABASE_MAIN_PATH)
        cursor = connect.cursor()

        cursor.execute(f"""
                        SELECT anothers
                        FROM messages
                        WHERE anothers LIKE "%{replied.message_id},%"
                        """)
        fetch = cursor.fetchone()

        if not fetch:
            cursor.execute(f"""
                            SELECT original
                            FROM messages
                            WHERE original LIKE "%{replied.message_id},%"
                            """)
            fetch = cursor.fetchone()
        
        fetch = fetch[0]

        original = str(message.id) + ','
        original += fetch.split(',')[1] + ','
        original += message.jump_url

        cursor.execute("""
                        INSERT INTO messages (original, anothers)
                        VALUES (?, ?)
                        """, (original, forwarded))
        connect.commit()
        connect.close()


async def on_edited(before: Message, after: Message):
    connect = con(deps.DATABASE_MAIN_PATH)
    connect.row_factory = Row
    cursor = connect.cursor()
    cursor.execute(
        """
        SELECT anothers
        FROM messages
        WHERE original LIKE ?
        """,
        (f"%{before.id},%",),
    )
    row = cursor.fetchone()
    connect.close()

    if not row:
        return

    forwarded = row['anothers'] if isinstance(row, Row) else row[0]
    forwarded_ids = [s for s in str(forwarded).split(';') if s]
    if not forwarded_ids:
        return

    fetches = give_fetch(before.channel.id)
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
            msg_id, url, _ = tuple(forw.split(','))
            webhook = Webhook.from_url(url, session=deps.global_http)
            try:
                mes = await webhook.fetch_message(int(msg_id))
                header = ''
                if mes.system_content.startswith('> -# Ответ на https://discord.com/channels'):
                    for i in mes.system_content:
                        header += i
                        if i == '\n':
                            break


                await webhook.edit_message(message_id=int(msg_id), content=header + after.content)
            except Exception:
                logging.exception('Failed to edit forwarded message')
