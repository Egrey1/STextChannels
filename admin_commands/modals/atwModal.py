from ..library import deps, Modal, TextInput, Interaction, Webhook, con, Row, Embed, List

class AtwModal(Modal):
    def __init__(self, web_name: str):
        super().__init__(title='Добаление нового канала к сети межсервера')

        self.channel_id = TextInput(
            label='Введите ID канала',
            placeholder='Пусто для выбора текущего канала',
            required=False,
            max_length=20
        )
        self.webhook_url = TextInput(
            label='Введите URL вебхука',
            placeholder='https://.......',
            required=True
        )
        self.web_name = web_name

        self.add_item(self.channel_id)
        self.add_item(self.webhook_url)
    
    async def on_submit(self, interaction: Interaction):
        channel_id = self.channel_id.value
        webhook_url = self.webhook_url.value

        if not channel_id:
            channel_id = interaction.channel_id

        try:
            webhook = Webhook.from_url(webhook_url)
            channel_id = int(channel_id)
        except ValueError:
            await interaction.response.send_message('Указан неверный URL')
            return
        except:
            await interaction.response.send_message('Неверно указан ID канала')
            return
        
        if channel_id != webhook.channel_id:
            await interaction.response.send_message('Указан неверный ID канала несоответсвующий вебхуку или наоборот')
            return

        connect = con(deps.DATABASE_MAIN_PATH)
        connect.row_factory = Row
        cursor = connect.cursor()

        cursor.execute("""
                       SELECT *
                       FROM shares
                       WHERE name = ?
                       """, (self.web_name))
        fetch = cursor.fetchone()
        
        if not fetch:
            connect.close()
            await interaction.response.send_message('Такого названия сети не существует!')
            return
        
        new_webhooks_url = fetch['webhooks_url'] + ';' + webhook_url
        new_text_channels = fetch['text_channels'] + ';' + str(channel_id)
        webhooks: List[Webhook] = []
        for url in new_webhooks_url.split(';'):
            try:
                webhooks.append(Webhook.from_url(url))
            except:
                continue

        cursor.execute("""
                       UPDATE shares
                       SET webhooks_url = ?, text_channels = ?
                       WHERE name = ?
                       """, (new_webhooks_url, new_text_channels, self.web_name))
        connect.commit()
        connect.close()

        embed = Embed(title='Сервер успешно добавлен! Вот новый список каналов:',
                      description='\n'.join(webhook.guild.name + webhook.channel.name for webhook in webhooks)
                      )

        await interaction.response.send_message(embed=embed)