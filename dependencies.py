from discord.ext.commands import Bot
from discord import Guild, Role, Intents
from aiohttp import ClientSession
from typing import Tuple, List
from sqlite3 import Connection

bot: Bot
intents: Intents
capital: Guild
PREFIX: Tuple[str]

TOKEN: str

DATABASE_MAIN_PATH: str
main_db: Connection

global_http: ClientSession
second_http: ClientSession

a_transguild: Role
m_transguild: Role

class Web:
    ...

class WebhookMessageSended:
    """
    Класс, представляющий одно отправленное вебхук-сообщение.

    Атрибуты:
        message_id (str): Уникальный идентификатор сообщения.
        webhook_url (str): URL вебхука, через который было отправлено сообщение.
        message_url (str): URL для просмотра сообщения (например, ссылка на Discord сообщение).
        author_id (str): Идентификатор автора сообщения.
        channel_id (str): Идентификатор канала, в котором было отправлено сообщение.
    """
    def __init__(
        self,
        message_id: int | str | None = None,
        webhook_url: str | None = None,
        message_url: str | None = None,
        author_id: int | str | None = None,
        channel_id: int | str | None = None
    ):
        """
        Инициализирует объект WebhookMessageSended.

        Объект может быть создан либо напрямую с передачей всех параметров,
        либо по одному из параметров — тогда данные будут загружены из базы данных.

        Параметры:
            message_id (int | str | None): ID сообщения. По умолчанию None.
            webhook_url (str | None): URL вебхука. По умолчанию None.
            message_url (str | None): URL сообщения. По умолчанию None.
            author_id (int | str | None): ID автора. По умолчанию None.
            channel_id (int | str | None): ID канала. По умолчанию None.

        Исключения:
            ValueError: Если не передано ни одного параметра или не найдено
                        соответствующей записи в базе данных.
        """
        self.message_id: str
        """Уникальный идентификатор сообщения.
        """
        self.webhook_url: str
        """URL вебхука, через который было отправлено сообщение.
        """
        self.message_url: str
        """URL для просмотра сообщения (например, ссылка на Discord сообщение).
        """
        self.author_id: str
        """Идентификатор автора сообщения.
        """
        self.channel_id: str
        """Идентификатор канала, в котором было отправлено сообщение.
        """

class WebhookMessagesSended:
    """
    Класс для управления группой вебхук-сообщений: оригинальным и связанными с ним.

    Атрибуты:
        original (WebhookMessageSended): Оригинальное сообщение.
        anothers (List[WebhookMessageSended]): Список связанных сообщений.
    """
    def __init__(
            self, 
            original: WebhookMessageSended = None, 
            anothers: List[WebhookMessageSended] = None, 
            message_id: int | str | None = None):
        """
        Инициализирует группу сообщений.

        Если передан message_id, данные загружаются из базы данных.
        В противном случае используются переданные original и anothers.

        Параметры:
            original (WebhookMessageSended | None): Оригинальное сообщение. По умолчанию None.
            anothers (List[WebhookMessageSended] | None): Список связанных сообщений. По умолчанию None.
            message_id (int | str | None): ID сообщения для поиска в БД. По умолчанию None.

        Исключения:
            ValueError: Если не найдена запись по message_id или некорректные данные.
        """
        self.original: WebhookMessageSended
        """Оригинальное сообщение.
        """
        self.anothers: List[WebhookMessageSended]
        """Список связанных сообщений.
        """

    def load(self):
        """
        Сохраняет текущую группу сообщений в базу данных.

        Формирует строки original и anothers и вставляет их в таблицу messages.
        Если запись уже существует, поведение зависит от схемы БД (возможно дублирование).

        Исключения:
            sqlite3.Error: При ошибках работы с базой данных.
        """