from discord.ext.commands import Bot, Context
from discord import Guild, Role, Intents, Message, TextChannel, SelectOption
from discord.ui import View
from aiohttp import ClientSession
from typing import Tuple, List, Dict
from sqlite3 import Connection

bot: Bot
intents: Intents
capital: Guild
PREFIX: Tuple[str]
commission: float

TOKEN: str

DATABASE_MAIN_PATH: str
DATABASE_ECONOMIC_PATH: str
main_db: Connection
economic_db: Connection

global_http: ClientSession
second_http: ClientSession

a_transguild: Role
m_transguild: Role
a_shop: Role
OPSK_role: Role
leader_role: Role

economicLogs: TextChannel

automod_exceptions: Tuple[str]

class CURRENCY:
    """Структура всех валют"""
    k: str = 'k'
    """Кредит"""
    kk: str = 'kk'
    """Красный кредит"""

class Web:
    """
    Класс для управления сетью (share) каналов с вебхуками.

    Атрибуты:
        name (str): Название сети.
        description (str): Описание сети.
        channels (str): Строка с каналами и вебхуками в формате 'id,url;id,url...'.
        groups (List[Dict[int, str]]): Список словарей с channel_id и webhook_url.
        bot (bool): Может ли сторонний бот отправлять сообщения в эту сеть.
    """
    def __init__(self, name: str | None = None):
        """
        Инициализирует объект Web по названию сети.

        Загружает данные из таблицы shares базы данных.

        Параметры:
            name (str | None): Название сети. По умолчанию None.

        Исключения:
            Exception: При ошибках базы данных.
        """
        self.name: str
        self.description: str
        self.channels: str
        self.groups: List[Dict[int, str]]
        self.bot: bool

    async def get_guilds(self) -> Tuple[Guild | None]:
        """
        Возвращает все сервера, подключенные к сети

        Returns:
        Tuple[Guild | None] - Кортеж всех серверов, подключенные к сети. None, если получить сервер не удалось
        """

    def set_name(self, new_name: str):
        """
        Устанавливает новое название сети и обновляет в базе данных.

        Параметры:
            new_name (str): Новое название сети.
        """

    def set_description(self, new_description: str):
        """
        Устанавливает новое описание сети и обновляет в базе данных.

        Параметры:
            new_description (str): Новое описание сети.
        """

    def set_channels(self, channels: str):
        """
        Устанавливает новые каналы и обновляет в базе данных.

        Параметры:
            channels (str): Строка с каналами в формате 'id,url;id,url...'.
        """
    
    def add_channel(self, channel_id: int, webhook_url: str):
        """
        Добавляет новый канал с вебхуком в сеть.

        Параметры:
            channel_id (int): ID канала.
            webhook_url (str): URL вебхука.
        """

    def set_bot(self, value: bool):
        """
        Устанавливает новое правило касаемо ботов

        Параметры:
            value (bool): Новое значение
        """

class WebhookMessageSended:
    """
    Класс, представляющий одно отправленное вебхук-сообщение.

    Атрибуты:
        message_id (str): Уникальный идентификатор сообщения.
        webhook_url (str): URL вебхука, через который было отправлено сообщение.
        message_url (str): URL для просмотра сообщения (например, ссылка на Discord сообщение).
        author_id (str): Идентификатор автора сообщения.
        channel_id (str): Идентификатор канала, в котором было отправлено сообщение.
        web (Web): Сеть, в рамках которого было отправлено это сообщение.
    """
    def __init__(
        self,
        message_id: int | str | None = None,
        webhook_url: str | None = None,
        message_url: str | None = None,
        author_id: int | str | None = None,
        channel_id: int | str | None = None,
        web: Web | str | None = None
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
            web (Web | str | None): Сеть, в рамках которого было отправлено это сообщение. По умолчанию None.

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
        self.web: Web
        """Сеть, в рамках которого было отправлено это сообщение.
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

    async def delete(self):
        """
        Удаляет все сообщения, которые были отправлены в этой сети.

        Удаляется так же запись в таблице messages.
        
        Исключения:
            Exception: При ошибках базы данных.
        """

class ShopItem:
    """
    Класс для представления товара в магазине.

    Атрибуты:
        name (str): Название товара.
        id (int): Уникальный ID товара.
        description (str): Описание товара.
        price (int): Цена товара.
        guild_id (int): ID гильдии, к которой относится товар.
        currency (str): Валюта товара.
    """
    def __init__(
            self, 
            name: str | None = None, 
            id_: int | None = None, 
            description: str | None = None, 
            price: int | None = None, 
            guild_id: int | None = None,
            currency: str | None = None,
            create: bool = False):
        """
        Инициализирует объект ShopItem.

        Если переданы name или id_, загружает данные из БД.
        Если create=True, создаёт новый товар в БД.

        Параметры:
            name (str | None): Название товара. По умолчанию None.
            id_ (int | None): ID товара. По умолчанию None.
            description (str | None): Описание товара. По умолчанию None.
            price (int | None): Цена товара. По умолчанию None.
            guild_id (int | None): ID гильдии. По умолчанию None.
            create (bool): Флаг создания нового товара или обновления текущего. По умолчанию False.

        Исключения:
            Exception: При ошибках базы данных.
        """
        self.name: str
        """Название товара"""
        self.id: int
        """Уникальный ID товара"""
        self.description: str
        """Описание товара"""
        self.price: int
        """Цена товара"""
        self.guild_id: int
        """ID гильдии, к которой относится товар"""
        self.currency: str
        """Валюта товара."""

class GuildShopItems:
    """
    Класс для списка товаров гильдии.

    Атрибуты:
        items (List[ShopItem]): Список товаров гильдии.
    """
    def __init__(self, guild_id: int):
        """
        Инициализирует объект GuildShopItems.

        Загружает все товары для указанной гильдии из БД.

        Параметры:
            guild_id (int): ID гильдии.

        Исключения:
            Exception: При ошибках базы данных.
        """
        self.items: List[ShopItem]
        """Список товаров гильдии"""


class Shop:
    """
    Класс для управления магазином гильдии.

    Атрибуты:
        ctx (Context): Контекст команды.
        guild_shop (GuildShopItems): Товары гильдии.
        items (List[ShopItem]): Список товаров.
        page (int): Текущая страница.
        per_page (int): Товаров на страницу.
        message (Message): Сообщение с магазином.
    """
    def __init__(self, ctx: Context):
        """
        Инициализирует объект Shop.

        Параметры:
            ctx (Context): Контекст команды.
        """
        self.guild_shop: GuildShopItems
        """Товары гильдии"""
        self.items: List[ShopItem]
        """Список товаров"""
        self.page: int
        """Текущая страница"""
        self.per_page: int
        """Товаров на страницу"""
        self.message: Message
        """Сообщение с магазином"""


class ItemsView(View):
    """
    View для интерфейса выбора товаров с пагинацией.

    Используется в командах редактирования и удаления товаров для выбора товара из списка.
    Поддерживает пагинацию с лимитом 12 опций на странице.

    Атрибуты:
        options (List[SelectOption]): Список опций для селекта.
        page (int): Текущая страница.
        per_page (int): Товаров на страницу (максимум 12).
        select_callback (callable): Асинхронная функция обратного вызова при выборе товара.
                                   Принимает Interaction в качестве параметра.
    """
    def __init__(self, options: List[SelectOption]):
        """
        Инициализирует ItemsView с пагинацией.

        Создаёт селект с плейсхолдером "Предметы" и кнопки навигации (⏮️ ⏭️),
        если товаров больше чем per_page.

        Параметры:
            options (List[SelectOption]): Список SelectOption для отображения.
                                         Каждый SelectOption содержит label (название товара)
                                         и value (ID товара).

        Пример использования:
            items = deps.GuildShopItems(ctx.guild.id).items
            options = [SelectOption(label=item.name, value=str(item.id)) for item in items]
            
            async def callback(interaction: Interaction):
                selected_id = interaction.data['values'][0]
                # Логика обработки выбранного товара
            
            view = ItemsView(options)
            view.select_callback = callback
            await ctx.send('Выберите предмет', view=view)
        """
        self.options: List[SelectOption]
        """Список опций для селекта"""
        self.page: int
        """Текущая страница"""
        self.per_page: int
        """Товаров на страницу (12)"""
        self.select_callback: callable
        """Функция обратного вызова при выборе. Должна быть асинхронной и принимать Interaction"""

class GuildPartner(Guild):
    """А документация потом!"""
    partner_name: str
    partner_piar_text: str
    partner_description: str
    channel: TextChannel
    marks: Tuple[str]
    message_id: int

    def __init__(self, partner_name: str, piar_text: str, desc: str, channel: TextChannel, marks: Tuple[str], id_: int, create: bool = False):
        """Инициализирует объект или создает/обновляет запись если create=True"""

    def change_name(self, name: str):
        """Изменяет имя партнера"""
    def change_piar_text(self, text: str):
        """Изменяет рекламный текст партнера"""
    def change_description(self, description: str):
        """Изменяет описание партнера"""
    def set_message_id(self, id_: int):
        """Устанавливает id партнерского сообщения"""