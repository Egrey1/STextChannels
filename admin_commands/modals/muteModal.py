from ..library import Modal, TextInput, Member, datetime, deps, logging, Interaction, Embed, AllowedMentions, View, Button

class MuteModal(Modal):
    def __init__(self, member_id: int, member: Member):
        super().__init__(title='Мьют участника межсервера')

        self.member_id = member_id
        self.member = member
        self.hours = TextInput(label='Час', placeholder='Целое число', required=False)
        self.minutes = TextInput(label='Минуты', placeholder='Целое число', required=False)
        self.seconds = TextInput(label='Секунда', placeholder='Целое число', required=False)
        self.where = TextInput(label='Где', placeholder='Каналы через запятую или all (по умолчанию)', required=False)
        self.reason = TextInput(label='Причина', placeholder='Укажите причину', required=True, max_length=512)

        self.add_item(self.hours)
        self.add_item(self.minutes)
        self.add_item(self.seconds)
        self.add_item(self.where)
        self.add_item(self.reason)

    async def on_submit(self, interaction: Interaction):
        now = datetime.datetime.now()
        hours = int(self.hours.value or 0)
        minutes = int(self.minutes.value or 0)
        seconds = int(self.seconds.value or 0)
        then = now + datetime.timedelta(
            hours=hours,
            minutes=minutes,
            seconds=seconds
        )
        # parse where field: support 'all', channel ids, or share names
        where_raw = (self.where.value or '').strip()
        if not where_raw:
            where_str = 'all'
        else:
            tokens = [t.strip() for t in where_raw.replace(',', ' ').split() if t.strip()]
            parsed = []
            for t in tokens:
                if t.lower() == 'all':
                    parsed = ['all']
                    break
                digits = ''.join(ch for ch in t if ch.isdigit())
                if digits:
                    parsed.append(digits)
                else:
                    # treat as share name (kept as-is)
                    parsed.append(t)
            where_str = ';'.join(parsed) if parsed else 'all'

        # apply mute directly via member_id (user may not be on this server)
        try:
            with deps.main_db as connect:
                cursor = connect.cursor()
                iso_time = then.isoformat()
                # set mute expiry
                cursor.execute(
                    """
                    INSERT INTO users (user_id, muted_up)
                    VALUES (?, ?)
                    ON CONFLICT(user_id) DO
                    UPDATE SET muted_up = excluded.muted_up
                    """,
                    (self.member_id, iso_time),
                )
                # set mute locations
                cursor.execute(
                    """
                    INSERT INTO users (user_id, where_muted)
                    VALUES (?, ?)
                    ON CONFLICT(user_id) DO
                    UPDATE SET where_muted = excluded.where_muted
                    """,
                    (self.member_id, where_str),
                )
                connect.commit()
                cursor.close()
            
            reason = self.reason.value
            
            embed = Embed(
                title='Мьют установлен!', 
                description=f"""Пользователь <@{self.member_id}> замьючен на:
                >>> {hours} {'часа' if hours < 5 and hours > 1 else 'час' if hours == 1 else 'часов'}
                {minutes} {'минуты' if minutes < 5 and minutes > 1 else 'минута' if minutes == 1 else 'минут'}
                {seconds} {'секунды' if seconds < 5 and seconds > 1 else 'секунда' if seconds == 1 else 'секунд'}"""
            )
            if reason:
                embed.add_field(name='Причина:', value=reason)
                try:
                    if self.member is None:
                        self.member = await deps.bot.fetch_user(self.member_id)
                    embed2 = Embed(title='Вас замьютили! Причина: ', description=reason)
                    embed2.set_footer(text=f'{interaction.user.global_name}: {'везде' if where_str == 'all' else where_str}', icon_url=interaction.user.avatar.url)
                    await self.member.send(embed=embed)
                except:
                    pass
            embed.set_footer(text=self.member_id, icon_url=interaction.user.avatar.url)

            await interaction.response.send_message(embed=embed)
            embed.title = f'<@{self.member_id}>'
            embed.set_footer(text=interaction.user.id, icon_url=interaction.user.avatar.url)

            view = View()
            button = Button(label='Откатить', emoji='🔁')

            button.callback = self.otkat_bt
            view.add_item(button)

            await deps.mutesLogs.send(embed=embed, view=view, allowed_mentions=AllowedMentions.none())
        except Exception as e:
            logging.error(f'Ошибка при установке мьюта: {e}')
            await interaction.response.send_message('Ошибка при установке мьюта', ephemeral=True)
            raise e

    async def otkat_bt(self, interaction: Interaction):
        if not (await interaction.user.is_a_transguild()):
            interaction.response.send_message('Ты не имеешь права пользоваться данной функцией', ephemeral=True)
            return
        
        id_ = interaction.message.embeds[0].footer.text
        try:
            with deps.main_db as connect:
                cursor = connect.cursor()

                cursor.execute("""
                               UPDATE users
                               SET where_muted = NULL, muted_up = NULL
                               WHERE user_id = ?
                               """, (id_, ))
                connect.commit()
                cursor.close()
            await interaction.response.send_message('Мьют успешно откачен!', ephemeral=True)
            await interaction.message.delete()
        except Exception as e:
            logging.error(f'Произошла ошибка в otkat_bt: {e}')
            await interaction.response.send_message('Произошла ошибка при попытке отката', ephemeral=True)
            raise e