from ..library import deps, Modal, TextInput, Interaction, Webhook, logging, Embed, List, TextStyle, TextChannel

class AtwAddModal(Modal):
    def __init__(self, web_name: str, manage_webhooks: bool):
        super().__init__(title='Добаление нового канала к сети межсервера')

        self.channel_id = TextInput(
            label='Введите ID канала',
            placeholder='Пусто для выбора текущего канала',
            required=False,
            max_length=20
        )
        self.webhook_url = TextInput(
            label='Введите URL вебхука',
            placeholder='https://.......' if not manage_webhooks else 'Пусто для автосоздания',
            required= not manage_webhooks
        )
        self.web_name = web_name
        self.manage_webhooks = manage_webhooks

        self.add_item(self.channel_id)
        self.add_item(self.webhook_url)
    
    async def on_submit(self, interaction: Interaction):
        channel_id = self.channel_id.value
        webhook_url = self.webhook_url.value

        if not channel_id:
            channel_id = interaction.channel_id

        if self.manage_webhooks and not webhook_url:
            webhook = await interaction.channel.create_webhook(name='Межсерверная сеть (телемост)', reason='Применено свойство автосоздания вебхука')
            webhook_url = webhook.url

        try:
            webhook = Webhook.from_url(webhook_url, session=deps.second_http)
            channel_id = int(channel_id)
        except ValueError:
            await interaction.response.send_message('Указан неверный URL')
            return
        except Exception as e:
            await interaction.response.send_message('Неверно указан ID канала')
            print(e)
            return
        
        # if channel_id != webhook.channel_id:
        #     await interaction.response.send_message('Указан неверный ID канала несоответсвующий вебхуку или наоборот')
        #     return

        try:
            with deps.main_db as connect:
                cursor = connect.cursor()

                cursor.execute(f"""
                            SELECT *
                            FROM shares
                            WHERE name = '{self.web_name}'
                            """)
                fetch = cursor.fetchone()
                
                if not fetch:
                    cursor.close()
                    await interaction.response.send_message('Такого названия сети не существует!')
                    return
                
                # new_webhooks_url = (fetch['webhooks_url'] + ';' + webhook_url) if fetch['webhooks_url'] else webhook_url
                # new_text_channels = (fetch['text_channels'] + ';' + str(channel_id)) if fetch['text_channels'] else str(channel_id)
                channels = fetch['channels']
                
                webhooks: List[Webhook] = []
                for url in channels.split(';') if channels else '':
                    try:
                        webhooks.append(Webhook.from_url(url.split(',')[1], session=deps.second_http))
                    except:
                        continue

                cursor.execute("""
                            UPDATE shares
                            SET channels = ?
                            WHERE name = ?
                            """, (
                                (channels + ';' + str(channel_id) + ',' + webhook_url) 
                                if channels else 
                                (str(channel_id) + ',' + webhook_url), 
                                self.web_name)
                                )
                connect.commit()
                cursor.close()

                web = deps.Web(self.web_name)
                channels: List[TextChannel] = []
                for channel in web.channels.split(';'):
                    channel = int(channel.split(',')[0])
                    try:
                        channels.append((await deps.bot.fetch_channel(channel)))
                    except:
                        continue

                embed = Embed(title='Сервер успешно добавлен! Вот новый список каналов:',
                            description='\n'.join(channel.guild.name + ' - ' + f'[{channel.name}]({channel.jump_url})' for channel in channels)
                            )
                embed.set_footer(text='Будьте внимательны! Проверка на ID канала вебхука и указанный ID отсутствует')

                await interaction.response.send_message(embed=embed)
        except Exception as e:
            logging.error(f'Ошибка в on_submit: {e}')

class AtwEditModal(Modal):
    def __init__(self, web_name):
        super().__init__(title='Изменение сети ' + web_name)
        self.web_name = web_name
        self.web = deps.Web(web_name)

        self.description = TextInput(label='Описание', style=TextStyle.paragraph, placeholder='Описание межсерверной сети', min_length=1, max_length=512, required=False)
        self.bot = TextInput(label='Может ли бот отправлять сообщения?', placeholder='0 для запрета, 1 для разрешения', max_length=1, required=False)

        self.add_item(self.description)
        self.add_item(self.bot)
    
    async def on_submit(self, interaction: Interaction):
        new_desc = self.description.value
        new_bot = False if self.bot.value == '0' else '1' if self.bot.value is not None else None

        if new_desc is None and new_bot is None:
            await interaction.response.send_message('Межсервер не был изменен!', ephemeral=True)
            return
        
        if new_desc is not None:
            self.web.set_description(new_desc)
        if new_bot is not None:
            self.web.set_bot(new_bot)
        
        await interaction.response.send_message('Изменения сохранены!', ephemeral=True)