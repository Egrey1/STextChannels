from ..library import Modal, TextInput, TextStyle, Interaction, deps, NotFound, logging, Message

class AddGPModal(Modal):
    def __init__(self, id_: int, edit_mode: bool = False):
        self.id_ = id_
        self.edit_mode = edit_mode
        super().__init__(title='Добавить новый сервер' if not edit_mode else 'Изменить сервер')

        self.name           = TextInput(label='Название сервера', placeholder='Введите название сервера', max_length=25, required= not edit_mode)
        self.piar_text      = TextInput(label='Текст пиара', placeholder='Введите текст пиара', max_length=1024, style=TextStyle.paragraph, required= not edit_mode)
        self.description    = TextInput(label='Описание', placeholder='Введите описание сервера', max_length=1024, style=TextStyle.paragraph, required= not edit_mode)
        self.add_item(self.name)
        self.add_item(self.piar_text)
        self.add_item(self.description)

        if not edit_mode:
            self.channel_id     = TextInput(label='Персональный канал', placeholder='Введите ID персонального канала на столичном сервере', max_length=32)
            self.avatar_url     = TextInput(label='Ссылка на аватар сервера', placeholder='...', required=False)
            self.add_item(self.avatar_url)
            self.add_item(self.channel_id)
        else:
            self.marks          = TextInput(label='Метки', placeholder='Введите метки сервера через ; без пробелов', max_length=512, required=False)
            self.add_item(self.marks)


    async def on_submit(self, interaction: Interaction):
        name = self.name.value
        piar_text = self.piar_text.value
        description = self.description.value
        if not self.edit_mode:
            channel_id = self.channel_id.value
            marks = tuple()
        else:
            marks = tuple(((self.marks.value).replace('; ', ';')).split(';'))

        guild = None
        try:
            guild = await deps.bot.fetch_guild(self.id_)
        except NotFound:
            pass

        try:
            channel_id = int(channel_id)
            channel = (await deps.capital.fetch_channel(channel_id))
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
        
        partner = deps.GuildPartner(name, piar_text, description, channel, marks, self.id_, True)

        if len(await channel.webhooks()) > 0:
            webhook = (await channel.webhooks())[0]
        else:
            webhook = (await channel.create_webhook(name=partner.partner_name))
        try:
            if not self.edit_mode:
                sent: Message = (await webhook.send(
                    content=partner.partner_piar_text, 
                    username=partner.partner_name, 
                    avatar_url=self.avatar_url.value if self.avatar_url.value else guild.icon.url if guild else None,
                    wait=True
                ))
                partner.set_message_id(sent.id)
            else:
                partner = deps.GuildPartner(name, piar_text, description, channel, marks, self.id_)
                try:
                    await webhook.edit_message(
                        message_id=partner.message_id,
                        content=partner.partner_piar_text
                    )
                except:
                    sent: Message = await webhook.send(
                        content=partner.partner_piar_text, 
                        username=partner.partner_name, 
                        avatar_url=guild.icon.url if guild else None,
                        wait=True
                        )
                    partner.set_message_id(sent)
        except Exception as e:
            logging.error(e)
            if not self.edit_mode:
                sent: Message = (await webhook.send(
                    content=partner.partner_piar_text, 
                    username=partner.partner_name, 
                    avatar_url=guild.icon.url if guild else None,
                    wait=True
                ))
                partner.set_message_id(sent.id)
            else:
                partner = deps.GuildPartner(name, piar_text, description, channel, marks, self.id_)
                try:
                    await webhook.edit_message(
                        message_id=partner.message_id,
                        content=partner.partner_piar_text
                    )
                except:
                    sent: Message = (await webhook.send(
                        content=partner.partner_piar_text, 
                        username=partner.partner_name, 
                        avatar_url=guild.icon.url if guild else None,
                        wait=True
                        ))
                    partner.set_message_id(sent)