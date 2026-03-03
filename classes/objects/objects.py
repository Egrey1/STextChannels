from ..library import con, deps, Row, List, Dict, logging

class Web:
    def __init__(self, name: str | None = None):
        try: 
            with deps.main_db as connect:
                cursor = connect.cursor()

                cursor.execute("""
                            SELECT *
                            FROM shares
                            WHERE name = ?
                            """, (name, ))
                fetch = cursor.fetchone()
                cursor.close()

                self.name = fetch['name']
                self.description = fetch['description']
                self.channels = fetch['channels']
                self.groups: List[Dict[int, str]]

                for group in fetch['channels']:
                    d = {
                        'channel_id': int(group.split(',')[0]),
                        'webhook_url': group.split(',')[1]
                    }
                    self.groups.append(d)
        except Exception as e:
            logging.error(f'Ошибка в Web: {e}')


    def set_name(self, new_name: str):
        try:
            with deps.main_db as connect:
                cursor = connect.cursor()

                cursor.execute("""
                            UPDATE shares
                            SET name = ?
                            WHERE name = ?
                            """, (new_name, self.name))
                connect.commit()
                cursor.close()
                self.name = new_name
        except Exception as e:
            logging.error(f'Ошибка в set_name: {e}')
    
    def set_description(self, new_description: str):
        try:
            with deps.main_db as connect:
                cursor = connect.cursor()

                cursor.execute("""
                            UPDATE shares
                            SET description = ?
                            WHERE name = ?
                            """, (new_description, self.name))
                connect.commit()
                cursor.close()
                self.description = new_description
        except Exception as e:
            logging.error(f'Ошибка в set_description: {e}')

    def set_channels(self, channels: str):
        try:
            with deps.main_db as connect:
                cursor = connect.cursor()

                cursor.execute("""
                            UPDATE shares
                            SET channels = ?
                            WHERE name = ?
                            """, (channels, self.name))
                connect.commit()
                cursor.close()
        except Exception as e:
            logging.error(f'Ошибка в set_channels: {e}')
    
    def add_channel(self, channel_id: int, webhook_url: str):
        try:
            with deps.main_db as connect:
                cursor = connect.cursor()

                self.channels = self.channels + ';' + str(channel_id) + ',' + webhook_url if self.channels else str(channel_id) + ',' + webhook_url

                cursor.execute("""
                            UPDATE shares
                            SET channels = ?
                            WHERE name = ?
                            """, (self.channels, self.name)
                            )
                connect.commit()
                cursor.close()

                self.groups.append(
                    {
                        'channel_id': channel_id,
                        'webhook_url': webhook_url
                    }
                )
        except Exception as e:
            logging.error(f'Ошибка в add_channel: {e}')

class WebhookMessageSended:
    
    def __init__(
            self, 
            message_id: int | str | None = None, 
            webhook_url: str | None = None, 
            message_url: str | None = None,
            author_id: int | str | None = None,
            channel_id: int | str | None = None):
        """
        Инициализирует объект WebhookMessageSended.

        Объект может быть создан либо напрямую с передачей всех параметров,
        либо по одному из параметров — тогда данные будут загружены из базы данных.

        Параметры:
            message_id (int | str | None): ID сообщения. По умолчанию None.
            webhook_url (str | None): URL вебхука. По умолчанию None.
            message_url (str | None): URL сообщения. По умолчанию None.
            author_id (int | str | None): ID автора. По умолчанию None.

        Исключения:
            ValueError: Если не передано ни одного параметра или не найдено
                        соответствующей записи в базе данных.
        """
        if (
        message_id is not None and
        webhook_url is not None and
        message_url is not None and
        author_id is not None and
        channel_id is not None
        ):
            self.message_id = str(message_id)
            self.webhook_url = webhook_url
            self.message_url = message_url
            self.author_id = str(author_id)
            self.channel_id = str(channel_id)
        else:
            try:
                with deps.main_db as connect:
                    cursor = connect.cursor()

                    need = (str(message_id) if message_id else
                            webhook_url if webhook_url else
                            message_url if message_url else
                            str(author_id) if author_id else 
                            str(channel_id) if channel_id else None)
                    
                    if need is None:
                        raise ValueError('Неправильные параметры конструктора')
                    
                    cursor.execute("""
                                    SELECT anothers
                                    FROM messages
                                    WHERE anothers LIKE ?
                                    """, ('%' + need + '%', ))
                    fetch = cursor.fetchone()[0]

                    if not fetch:
                        cursor.execute("""
                                    SELECT original
                                    FROM messages
                                    WHERE anothers LIKE ?
                                    """, ('%' + need + '%', ))
                        fetch = cursor.fetchone()[0]
                        cursor.close()
                        if not fetch:
                            raise ValueError('Неправильные параметры конструктора')
                        
                        splited = fetch.split(',')
                    else:
                        cursor.close()
                        ineed = fetch.find(need)
                        fneed = fetch.find(need, ineed)
                        lneed = fetch.rfind(need, 0, ineed)
                        splited = fetch[fneed+1 : lneed].split(',')

                    self.message_id, self.webhook_url, self.message_url, self.author_id, self.channel_id = (
                    splited[0], splited[1], splited[2], splited[3], splited[4])
            except Exception as e:
                logging.error(f'Ошибка в WebhookMessageSenden: {e}')


class WebhookMessagesSended:
    def __init__(self, original: WebhookMessageSended = None, anothers: List[WebhookMessageSended] = None, message_id: int | str | None = None):
        if message_id is None:
            self.original = original
            self.anothers = anothers
        else:
            try:
                with deps.main_db as connect:
                    connect.row_factory = Row
                    cursor = connect.cursor()

                    cursor.execute("""
                                SELECT *
                                FROM messages
                                WHERE original LIKE ?
                                OR anothers LIKE ?
                                """, (f'%{message_id}%', f'%{message_id}%'))
                    fetch = cursor.fetchone()
                    cursor.close()

                    if not fetch:
                        raise ValueError('Неправильные параметры конструктора')
                    original = fetch['original']
                    anothers = fetch['anothers']

                    original = WebhookMessageSended(
                                        original.split(',')[0], 
                                        original.split(',')[1], 
                                        original.split(',')[2], 
                                        original.split(',')[3],
                                        original.split(',')[4])
                    new_anothers = []
                    for another in anothers.split(';'):
                        new_anothers.append(WebhookMessageSended(
                                            another.split(',')[0], 
                                            another.split(',')[1], 
                                            another.split(',')[2], 
                                            another.split(',')[3],
                                            another.split(',')[4]))
                    self.original = original
                    self.anothers: List[WebhookMessageSended] = new_anothers
            except Exception as e:
                logging.error(f'Ошибка в WebhookMessagesSended: {e}')


    def load(self):
        original = self.original.message_id + ','
        original += self.original.webhook_url + ','
        original += self.original.message_url + ','
        original += self.original.author_id + ','
        original += self.original.channel_id

        anothers = ''
        for another in range(len(self.anothers)):
            anothers += self.anothers[another].message_id + ','
            anothers += self.anothers[another].webhook_url + ','
            anothers += self.anothers[another].message_url + ','
            anothers += self.anothers[another].author_id + ','
            anothers += self.anothers[another].channel_id
            anothers += ';' if another != len(self.anothers) - 1 else ''

        try:
            with deps.main_db as connect:
                cursor = connect.cursor()

                cursor.execute("""
                            INSERT INTO messages (original, anothers)
                            VALUES (?, ?)
                            """, (original, anothers))
                connect.commit()
                cursor.close()
        except Exception as e:
            logging.info(f'Ошибка в load: {e}')