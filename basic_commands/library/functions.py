from .modules import Message, con, Row, deps, Webhook, logging, AllowedMentions, List


def give_fetch(channel_id: int) -> List[dict] | None:
    try:
        with deps.main_db as connect:
            cursor = connect.cursor()
            cursor.execute(
                """
                SELECT *
                FROM shares
                """
            )
            fetches = cursor.fetchall()
            cursor.close()

            result: List[dict] = []

            for fetch in fetches:
                fetch = dict(fetch) 
                if not fetch['channels']:
                    continue
                
                channels = fetch.get('channels', ';').split(';')
                for channel in channels:
                    if str(channel_id) in channel.split(','):
                        result.append(fetch)

            return result if result else None
    except Exception as e:
        logging.error(f'Ошибка в give_fetch: {e}')
        return None


async def on_sended(message: Message):
    fetches = give_fetch(message.channel.id)
    if not fetches:
        return

    for fetch in fetches:
        original: deps.WebhookMessageSended
        urls = []
        
        for u in dict(fetch).get('channels', '').split(';'):
            if u.split(',')[0] == str(message.channel.id):
                original = deps.WebhookMessageSended(
                    message.id, 
                    u.split(',')[1], 
                    message.jump_url, 
                    message.author.id,
                    message.channel.id)
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

        anothers: List[deps.WebhookMessageSended] = []
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
                    anothers.append(
                        deps.WebhookMessageSended(
                            sent.id, 
                            webhook.url, 
                            sent.jump_url, 
                            message.author.id,
                            sent.channel.id)
                    )
            except Exception:
                logging.exception('Failed to send message via webhook')

        if anothers and original:
            tmp = deps.WebhookMessagesSended(original, anothers)
            tmp.load()

async def on_sended_replaied(message: Message):
    replied = message.reference

    webhook_m_s = deps.WebhookMessagesSended(message_id=replied.message_id)

    # connect = con(deps.DATABASE_MAIN_PATH)
    # connect.row_factory = Row
    # cursor = connect.cursor()

    # cursor.execute("""
    #                 SELECT *
    #                 FROM messages
    #                 WHERE original LIKE ?
    #                 OR anothers LIKE ?
    #                 """, (f"%{replied.message_id},%", f"%{replied.message_id},%"))
    # fetches = cursor.fetchall()
    # connect.close()

    if not hasattr(webhook_m_s.anothers):
        return

    if not (webhook_m_s.anothers and webhook_m_s.original):
        return
    
    # sent_ids = []

    sendes = webhook_m_s.anothers
    sendes.append(webhook_m_s.original)
    original: deps.WebhookMessageSended
    anothers: List[deps.WebhookMessageSended] = []

    for webmes in sendes:
        if webmes.channel_id == str(message.channel.id):
            original = deps.WebhookMessageSended(
                message.id, 
                webmes.webhook_url, 
                message.jump_url, 
                message.author.id,
                message.channel.id
            )
            continue

        files = [
            await attachment.to_file() 
            for attachment in message.attachments] if message.attachments else []
        
        webhook: Webhook = Webhook.from_url(webmes.webhook_url, session=deps.global_http)

        sent: Message = await webhook.send(
                    content=f'> -# Ответ на {webmes.message_url}\n\n' + message.content,
                    username=message.author.global_name,
                    avatar_url=message.author.display_avatar.url,
                    files=files[:10],
                    wait=True,
                    allowed_mentions=AllowedMentions.none()
                )
        
        if sent.channel.id == message.channel.id:
            original = deps.WebhookMessageSended(
                message.id, 
                webmes.webhook_url, 
                message.jump_url, 
                message.author.id,
                message.channel.id
            )
            await sent.delete()
        else:
            anothers.append(deps.WebhookMessageSended(
                sent.id, 
                webhook.url, 
                sent.jump_url, 
                message.author.id, 
                message.channel.id))

        

    if anothers and original:
        tmp = deps.WebhookMessagesSended(original, anothers)
        tmp.load()


async def on_edited(before: Message, after: Message):
    try:
        with deps.main_db as connect:
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
            cursor.close()
    except Exception as e:
        logging.error(f'Ошибка в on_edited: {e}')
        return

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
            msg_id, url = forw.split(',')[0], forw.split(',')[1]
            webhook = Webhook.from_url(url, session=deps.global_http)
            try:
                mes = await webhook.fetch_message(int(msg_id))
                header = ''
                if mes.system_content.startswith('> -# Ответ на https://discord.com/channels'):
                    for i in mes.system_content:
                        header += i
                        if i == '\n':
                            break


                await webhook.edit_message(message_id=int(msg_id), content=header + '\n' + after.content)
            except Exception:
                logging.exception('Failed to edit forwarded message')
