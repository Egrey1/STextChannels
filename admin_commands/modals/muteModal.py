from ..library import Modal, TextInput, Member, datetime, deps, logging

class MuteModal(Modal):
    def __init__(self, member_id: int):
        super().__init__(title='Мьют участника межсервера')

        self.member_id = member_id
        self.days = TextInput(label='День', placeholder='Целое число', required=False)
        self.hours = TextInput(label='Час', placeholder='Целое число', required=False)
        self.minutes = TextInput(label='Минуты', placeholder='Целое число', required=False)
        self.seconds = TextInput(label='Секунда', placeholder='Целое число', required=False)
        self.where = TextInput(label='Где', placeholder='Каналы через запятую или all (по умолчанию)', required=False)

        self.add_item(self.days)
        self.add_item(self.hours)
        self.add_item(self.minutes)
        self.add_item(self.seconds)
        self.add_item(self.where)

    async def on_submit(self, interaction):
        now = datetime.datetime.now()
        then = now + datetime.timedelta(
            days=int(self.days.value or 0),
            hours=int(self.hours.value or 0),
            minutes=int(self.minutes.value or 0),
            seconds=int(self.seconds.value or 0)
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
            await interaction.response.send_message('Мьют установлен', ephemeral=True)
        except Exception as e:
            logging.error(f'Ошибка при установке мьюта: {e}')
            await interaction.response.send_message('Ошибка при установке мьюта', ephemeral=True)

