from ..library import con, deps, Row, List, Dict, logging, TextChannel, Tuple, Webhook
from discord import Embed, ui, ButtonStyle, SelectOption, Interaction, Guild
from discord.ext.commands import Context

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

                if not fetch:
                    raise ValueError('Неверные параметры конструктора')

                self.name = fetch['name']
                self.description = fetch['description']
                self.channels = fetch['channels']
                self.groups: List[Dict[int, str]] = []
                self.bot = bool(fetch['bots'])

                for group in fetch['channels'].split(';'):
                    d = {
                        'channel_id': int(group.split(',')[0]),
                        'webhook_url': group.split(',')[1]
                    }
                    self.groups.append(d)
        except Exception as e:
            logging.error(f'Ошибка в Web: {e}')
            raise e

    async def get_guilds(self):
        guilds = []
        for channel in self.channels.split(';'):
            channel_id = channel.split(',')[0]
            try:
                guild = (await deps.bot.fetch_channel(int(channel_id))).guild
                guilds.append(guild)
            except:
                guilds.append(None)


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

    def set_bot(self, value: bool):
        try:
            with deps.main_db as connect:
                cursor = connect.cursor()

                cursor.execute("""
                               UPDATE shares
                               SET bots = ?
                               WHERE name = ?
                               """, ('1' if value else None, self.name))
                connect.commit()
                cursor.close()

                self.bot = value
        except Exception as e:
            logging.error(f'Ошибка в set_bot: {e}')
            raise e

class WebhookMessageSended:
    
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

        Исключения:
            ValueError: Если не передано ни одного параметра или не найдено
                        соответствующей записи в базе данных.
        """
        if (
        message_id is not None and
        webhook_url is not None and
        message_url is not None and
        author_id is not None and
        channel_id is not None and
        web is not None
        ):
            self.message_id = str(message_id)
            self.webhook_url = webhook_url
            self.message_url = message_url
            self.author_id = str(author_id)
            self.channel_id = str(channel_id)
            self.web = web if isinstance(web, Web) else Web(web)
        else:
            try:
                with deps.main_db as connect:
                    cursor = connect.cursor()

                    need = (str(message_id) if message_id else
                            webhook_url if webhook_url else
                            message_url if message_url else
                            str(author_id) if author_id else 
                            str(channel_id) if channel_id else 
                            web.name if web else None)
                    
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

                    self.message_id, self.webhook_url, self.message_url, self.author_id, self.channel_id, self.web = (
                    splited[0], splited[1], splited[2], splited[3], splited[4], Web(splited[5]))
            except Exception as e:
                logging.error(f'Ошибка в WebhookMessageSended: {e}')
                raise ValueError(f'Ошибка в WebhookMessageSended: {e}')


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
                                        original.split(',')[4],
                                        original.split(',')[5]
                    )
                    new_anothers = []
                    for another in anothers.split(';'):
                        new_anothers.append(WebhookMessageSended(
                                            another.split(',')[0], 
                                            another.split(',')[1], 
                                            another.split(',')[2], 
                                            another.split(',')[3],
                                            another.split(',')[4],
                                            another.split(',')[5]
                        ))
                    self.original = original
                    self.anothers: List[WebhookMessageSended] = new_anothers
            except Exception as e:
                logging.error(f'Ошибка в WebhookMessagesSended: {e}')
                raise ValueError(f'Ошибка в WebhookMessagesSended: {e}')


    def load(self):
        original = self.original.message_id + ','
        original += self.original.webhook_url + ','
        original += self.original.message_url + ','
        original += self.original.author_id + ','
        original += self.original.channel_id + ','
        original += self.original.web.name

        anothers = ''
        for another in range(len(self.anothers)):
            anothers += self.anothers[another].message_id + ','
            anothers += self.anothers[another].webhook_url + ','
            anothers += self.anothers[another].message_url + ','
            anothers += self.anothers[another].author_id + ','
            anothers += self.anothers[another].channel_id + ','
            anothers += self.anothers[another].web.name
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
            raise ValueError(f'Ошибка в load: {e}')
        
    async def delete(self):
        try:
            for another in (self.anothers + [self.original]):
                try:
                    webhook = Webhook.from_url(another.webhook_url, session=deps.global_http)
                    await webhook.delete_message(int(another.message_id))
                except:
                    continue
            
            with deps.main_db as connect:
                cursor = connect.cursor()

                cursor.execute("""
                                DELETE FROM messages
                                    WHERE rowid IN (
                                    SELECT rowid
                                    FROM messages
                                    WHERE original LIKE ?
                                    LIMIT 1
                                );
                               """, (f'%{self.original.message_id}%',))
                connect.commit()
                cursor.close()
        except Exception as e:
            logging.info(f'Ошибка в delete: {e}')


class ShopItem:
    """
    Класс для представления товара в магазине.

    Атрибуты:
        name (str): Название товара.
        id (int): Уникальный ID товара.
        description (str): Описание товара.
        price (int): Цена товара.
        guild_id (int): ID гильдии, к которой относится товар.
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
            create (bool): Флаг создания нового товара. По умолчанию False.

        Исключения:
            Exception: При ошибках базы данных.
        """
        try:
            with deps.economic_db as connect:
                cursor = connect.cursor()

                if name is not None and id_ is None:
                    cursor.execute("""
                                   SELECT * 
                                   FROM shop
                                   WHERE item_name = ?
                                   """, (name, ))
                elif id_ is not  None and name is None:
                    cursor.execute("""
                                   SELECT *
                                   FROM shop
                                   WHERE item_id = ?
                                   """, (id_, ))
                else:
                    self.name = name
                    self.id = id_
                    self.description = description
                    self.price = price
                    self.guild_id = guild_id
                    self.currency = currency
                    if not create:
                        cursor.close()
                        return
                    
                    cursor.execute("""
                                   INSERT INTO shop (item_name, item_id, description, price, guild_id, currency)
                                   VALUES (?, ?, ?, ?, ?, ?)
                                   ON CONFLICT(item_id) DO
                                   UPDATE SET 
                                   item_name = excluded.item_name, 
                                   description = excluded.description, 
                                   price = excluded.price, 
                                   guild_id = excluded.guild_id,
                                   currency = excluded.currency
                                   """, (self.name, self.id, self.description, self.price, self.guild_id))
                    connect.commit()
                    cursor.close()
                    return
                
                fetch = cursor.fetchone()
                cursor.close()

                if not fetch:
                    self.name = None
                    self.id = None
                    self.description = None
                    self.price = None
                    self.guild_id = None
                    self.currency = None
                    logging.error(f'Запись в БД не найдена! {id_ if id_ else name}')
                    return

                self.name = fetch['item_name']
                self.id = fetch['item_id']
                self.description = fetch['description']
                self.price = fetch['price']
                self.guild_id = fetch['guild_id']
                self.currency = fetch['currency']
        except Exception as e:
            logging.error(f'Ошибка в ShopItem: {e}')

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
        try:
            with deps.economic_db as connect:
                cursor = connect.cursor()

                cursor.execute("""
                                SELECT *
                                FROM shop
                                WHERE guild_id = ?
                               """, (guild_id, ))
                
                fetches = cursor.fetchall()
                cursor.close()

                self.items: List[ShopItem] = []
                for fetch in fetches:
                    self.items.append(
                                ShopItem(
                                        fetch['item_name'], 
                                        fetch['item_id'], 
                                        fetch['description'], 
                                        fetch['price'], 
                                        fetch['guild_id'],
                                        fetch['currency']))
        except Exception as e:
            logging.error(f'Ошибка в GuildShopItems: {e}')

class ShopView(ui.View):
    """
    View для интерфейса магазина с кнопками и селектом.

    Атрибуты:
        shop (Shop): Экземпляр Shop для доступа к данным.
    """
    def __init__(self, shop: 'Shop'):
        """
        Инициализирует ShopView.

        Создаёт селект и кнопки навигации, если нужно.

        Параметры:
            shop (Shop): Экземпляр Shop.
        """
        super().__init__(timeout=300)
        self.shop = shop
        select = self.shop.create_select()
        select.callback = self.select_callback

        self.add_item(select)
        if len(self.shop.items) > self.shop.per_page:
            prev_button = ui.Button(label="⏮️", style=ButtonStyle.primary, disabled=True)
            next_button = ui.Button(label="⏭️", style=ButtonStyle.primary)
            prev_button.callback = self.prev_callback
            next_button.callback = self.next_callback
            self.add_item(prev_button)
            self.add_item(next_button)

    async def prev_callback(self, interaction: Interaction):
        """
        Обработчик кнопки Previous.

        Переходит на предыдущую страницу.
        """
        if self.shop.page > 0:
            self.shop.page -= 1
            embed = self.shop.create_embed()
            select = self.shop.create_select()
            select.callback = self.select_callback
            self.clear_items()
            self.add_item(select)
            if len(self.shop.items) > self.shop.per_page:
                prev_button = ui.Button(label="⏮️", style=ButtonStyle.primary, disabled=self.shop.page == 0)
                next_button = ui.Button(label="⏭️", style=ButtonStyle.primary, disabled=self.shop.page >= len(self.shop.items) // self.shop.per_page)
                prev_button.callback = self.prev_callback
                next_button.callback = self.next_callback
                self.add_item(prev_button)
                self.add_item(next_button)
            await interaction.response.edit_message(embed=embed, view=self)

    async def next_callback(self, interaction: Interaction):
        """
        Обработчик кнопки Next.

        Переходит на следующую страницу.
        """
        if (self.shop.page + 1) * self.shop.per_page < len(self.shop.items):
            self.shop.page += 1
            embed = self.shop.create_embed()
            select = self.shop.create_select()
            select.callback = self.select_callback
            self.clear_items()
            self.add_item(select)
            if len(self.shop.items) > self.shop.per_page:
                prev_button = ui.Button(label="⏮️", style=ButtonStyle.primary, disabled=self.shop.page == 0)
                next_button = ui.Button(label="⏭️", style=ButtonStyle.primary, disabled=self.shop.page >= len(self.shop.items) // self.shop.per_page)
                prev_button.callback = self.prev_callback
                next_button.callback = self.next_callback
                self.add_item(prev_button)
                self.add_item(next_button)
            await interaction.response.edit_message(embed=embed, view=self)

    async def select_callback(self, interaction: Interaction):
        """
        Обработчик выбора товара в селекте.

        Отправляет embed с информацией о товаре и админах.
        """
        selected_value = interaction.data['values'][0]
        item = ShopItem(id_=int(selected_value))

        embed = Embed(
            title=item.name + ' - ' + str(item.price) + ' ' + (
                'кредитов' if item.price > 4 else 'кредит' if item.price == 1 else 'кредита'
                ), description=item.description)
        
        embed.set_footer(text=interaction.user.display_name, icon_url=interaction.user.display_avatar.url)

        async def bt_callback(interaction: Interaction):
            if not (await interaction.user.is_a_shop()):
                await interaction.response.send_message('Вы не имеете право использовать эту кнопку!', ephemeral=True)
                return
            user = interaction.user
            if user.get_money() < item.price:
                await interaction.response.send_message(f'У {user.mention} недостаточно кредитов для покупки предмета!')
                return
            
            await user.add_money(-item.price)
            await interaction.guild.add_money(item.price * deps.commission)

            await interaction.response.send_message(f'Оплата была произведена успешно! Баланс сервера увеличился на {(item.price * deps.commission):.2f} и теперь равен {(interaction.guild.get_money()):.2f}')

        view = ui.View()
        button = ui.Button(label='Разрешить покупку', emoji='✅')

        button.callback = bt_callback
        view.add_item(button)

        await interaction.response.send_message(f"Ожидайте прибытия АММ", embed=embed, view=view)


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
    def __init__(self, ctx: Context, guild_id: int | None = None):
        """
        Инициализирует объект Shop.

        Параметры:
            ctx (Context): Контекст команды.
        """
        self.ctx = ctx
        self.guild_shop = GuildShopItems(ctx.guild.id if guild_id is None else guild_id)
        self.items = self.guild_shop.items
        self.page = 0
        self.per_page = 10
        self.message = None

    def create_embed(self):
        """
        Создаёт embed для текущей страницы товаров.

        Возвращает:
            Embed: Embed с товарами.
        """
        embed = Embed(title="Shop", color=0x00ff00)
        start = self.page * self.per_page
        end = start + self.per_page
        page_items = self.items[start:end]
        for item in page_items:
            embed.add_field(
                name=f"{item.name} - {item.price}{item.currency}",
                value=item.description,
                inline=False
            )
        embed.set_footer(text=f"Page {self.page + 1} of {(len(self.items) - 1) // self.per_page + 1}")
        return embed

    def create_select(self):
        """
        Создаёт селект для текущей страницы товаров.

        Возвращает:
            Select: Селект с опциями товаров.
        """
        start = self.page * self.per_page
        end = start + self.per_page
        page_items = self.items[start:end]
        options = [
            SelectOption(
                label=item.name,
                value=str(item.id),
                description=item.description[:100] if item.description else ""
            ) for item in page_items
        ]
        select = ui.Select(placeholder="Выберите предмет для покупку", options=options)
        return select

    async def send(self):
        """
        Отправляет сообщение с магазином в канал.
        """
        embed = self.create_embed()
        view = ShopView(self)
        if not self.guild_shop.items:
            await self.ctx.send('Товары отсутствуют!')
            return
        self.message = await self.ctx.send(embed=embed, view=view)


class ItemsView(ui.View):
    """
    View для интерфейса выбора товаров с пагинацией.

    Атрибуты:
        options (List[SelectOption]): Список опций для селекта.
        page (int): Текущая страница.
        per_page (int): Товаров на страницу (максимум 12).
        select_callback (callable): Функция обратного вызова при выборе товара.
    """
    def __init__(self, options: List[SelectOption]):
        """
        Инициализирует ItemsView с пагинацией.

        Создаёт селект и кнопки навигации для выбора товаров.

        Параметры:
            options (List[SelectOption]): Список SelectOption для отображения.
        """
        super().__init__(timeout=300)
        self.options = options
        self.page = 0
        self.per_page = 12
        self.select_callback = None  # Будет установлена снаружи
        
        self._update_view()

    def _create_select(self):
        """
        Создаёт селект для текущей страницы опций.

        Возвращает:
            Select: Селект с опциями текущей страницы.
        """
        start = self.page * self.per_page
        end = start + self.per_page
        page_options = self.options[start:end]
        
        select = ui.Select(
            placeholder="Предметы",
            options=page_options,
            min_values=1,
            max_values=1
        )
        select.callback = self._select_handler
        return select

    async def _select_handler(self, interaction: Interaction):
        """
        Внутренний обработчик выбора селекта.

        Вызывает установленный select_callback если он существует.
        """
        if self.select_callback:
            await self.select_callback(interaction)

    def _update_view(self):
        """
        Обновляет компоненты view (селект и кнопки навигации).
        """
        self.clear_items()
        
        select = self._create_select()
        self.add_item(select)
        
        # Добавляем кнопки навигации, если нужна пагинация
        if len(self.options) > self.per_page:
            prev_button = ui.Button(label="⏮️", style=ButtonStyle.primary, disabled=self.page == 0)
            next_button = ui.Button(label="⏭️", style=ButtonStyle.primary, disabled=self.page >= (len(self.options) - 1) // self.per_page)
            
            prev_button.callback = self.prev_callback
            next_button.callback = self.next_callback
            
            self.add_item(prev_button)
            self.add_item(next_button)

    async def prev_callback(self, interaction: Interaction):
        """
        Обработчик кнопки Previous.

        Переходит на предыдущую страницу и обновляет селект.
        """
        if self.page > 0:
            self.page -= 1
            self._update_view()
            await interaction.response.edit_message(view=self)

    async def next_callback(self, interaction: Interaction):
        """
        Обработчик кнопки Next.

        Переходит на следующую страницу и обновляет селект.
        """
        if (self.page + 1) * self.per_page < len(self.options):
            self.page += 1
            self._update_view()
            await interaction.response.edit_message(view=self)


class GuildPartner():
    def __init__(self, partner_name: str, piar_text: str, desc: str, channel: TextChannel, marks: Tuple[str], id_: int | None, create: bool = False):
        if not (partner_name or piar_text or desc or channel or marks):
            logging.error('Пустые данные')
            return
        
        self.partner_name           = partner_name
        self.partner_piar_text      = piar_text
        self.partner_description    = desc
        self.channel                = channel
        self.marks                  = marks
        self.id                     = id_

        try:
            with deps.main_db as connect:
                if create:
                    cursor = connect.cursor()

                    cursor.execute("""
                                   INSERT INTO `guild-partner` (name, piar_text, description, channel_id, marks, id)
                                   VALUES (?, ?, ?, ?, ?, ?)
                                   ON CONFLICT 
                                   DO UPDATE SET name = excluded.name, piar_text = excluded.piar_text, description = excluded.description, channel_id = excluded.channel_id, marks = excluded.marks
                                   """, (self.partner_name, self.partner_piar_text, self.partner_description, self.channel.id, ';'.join(marks), self.id ))
                    connect.commit()
                    cursor.close()
                else:
                    cursor = connect.cursor()
                    cursor.execute("""
                                   SELECT *
                                   FROM `guild-partner`
                                   WHERE id = ?
                                   """, (self.id))
                    self.message_id = int(cursor.fetchone()['message_id'])
            
        except Exception as e:
            logging.error(f'Ошибка в GuildPartner: {e}')

    def change_name(self, new_name):
        try:
            with deps.main_db as connect:
                cursor = connect.cursor()

                cursor.execute("""
                               UPDATE guild-partner
                               SET name = ?
                               WHERE id = ?
                               """, (new_name, self.id))
                connect.commit()
                cursor.close()
                self.partner_name = new_name
        except Exception as e:
            logging.error(f'Ошибка в change_name: {e}')
    
    def change_piar_text(self, piar_text):
        try:
            with deps.main_db as connect:
                cursor = connect.cursor()

                cursor.execute("""
                               UPDATE guild-partner
                               SET piar_text = ?
                               WHERE id = ?
                               """, (piar_text, self.id))
                connect.commit()
                cursor.close()
                self.partner_piar_text = piar_text
        except Exception as e:
            logging.error(f'Ошибка в change_piar_text: {e}')

    def change_description(self, description):
        try:
            with deps.main_db as connect:
                cursor = connect.cursor()

                cursor.execute("""
                               UPDATE guild-partner
                               SET description = ?
                               WHERE id = ?
                               """, (description, self.id))
                connect.commit()
                cursor.close()
                self.partner_piar_text = description
        except Exception as e:
            logging.error(f'Ошибка в change_description: {e}')

    def set_message_id(self, id_: int):
        try:
            with deps.main_db as connect:
                cursor = connect.cursor()

                cursor.execute("""
                               UPDATE `guild-partner`
                               SET message_id = ?
                               WHERE id = ?
                               """, (id_, self.id))
                connect.commit()
                cursor.close()
        except Exception as e:
            logging.error(f'Ошибка в set_message_id: {e}')
