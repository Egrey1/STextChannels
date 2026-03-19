from ..library import Modal, TextInput, TextStyle, Interaction, deps, NotFound, logging

class AddGPModal(Modal):
    def __init__(self, id_: int):
        self.id_ = id_
        super().__init__(title='Добавить новый сервер')

        self.name           = TextInput(label='Название сервера', placeholder='Введите название сервера', max_length=25)
        self.piar_text      = TextInput(label='Текст пиара', placeholder='Введите текст пиара', max_length=1024, style=TextStyle.paragraph)
        self.description    = TextInput(label='Описание', placeholder='Введите описание сервера', max_length=1024, style=TextStyle.paragraph)
        self.channel_id     = TextInput(label='Персональный канал', placeholder='Введите ID персонального канала на столичном сервере', max_length=32)
        self.marks          = TextInput(label='Метки', placeholder='Введите метки сервера через ; без пробелов', max_length=512)

        self.add_item(self.name)
        self.add_item(self.piar_text)
        self.add_item(self.description)
        self.add_item(self.channel_id)
        self.add_item(self.marks)

    async def on_submit(self, interaction: Interaction):
        name = self.name.value
        piar_text = self.piar_text.value
        description = self.description.value
        channel_id = self.channel_id.value
        marks = tuple(((self.marks.value).replace('; ', ';')).split(';'))
        try:
            guild = await deps.bot.fetch_guild(self.id_)
        except NotFound:
            await interaction.response.send_message('Сервер не найден!', ephemeral=True)
            return

        try:
            channel_id = int(channel_id)
            channel = (await deps.bot.fetch_channel(channel_id))
        except ValueError:
            await interaction.response.send_message('ID канала не является числом!', ephemeral=True)
            return
        except NotFound: 
            await interaction.response.send_message('Канал не найден!', ephemeral=True)
            return 
        except Exception as e:
            await interaction.response.send_message('Неизвестная ошибка!', ephemeral=True)
            logging.error(f'Неизвесная ошибка: {e}')
            return
        
        partner = deps.GuildPartner(name, piar_text, description, channel, marks, self.id_, True, interaction.guild)

        if len(await channel.webhooks()) > 0:
            webhook = (await channel.webhooks())[0]
        else:
            webhook = (await channel.create_webhook(name=partner.partner_name, avatar=partner.icon))
        await webhook.send(content=partner.partner_piar_text, username=partner.partner_name, avatar_url=partner.icon.url)
