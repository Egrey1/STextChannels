from ..library import Modal, TextInput, Member, datetime

class MuteModal(Modal):
    def __init__(self, member: Member):
        super().__init__(title='Мьют участника межсервера')

        self.member = member
        self.days = TextInput(label='День', placeholder='Целое число', required=False)
        self.hours = TextInput(label='Час', placeholder='Целое число', required=False)
        self.minutes = TextInput(label='Минуты', placeholder='Целое число', required=False)
        self.seconds = TextInput(label='Секунда', placeholder='Целое число', required=False)
        # self.where = TextInput(label='Где', placeholder='Название межсервера или этот канал (если пусто)', required=False)

        self.add_item(self.days)
        self.add_item(self.hours)
        self.add_item(self.minutes)
        self.add_item(self.seconds)
        # self.add_item(self.where)

    async def on_submit(self):
        now = datetime.datetime.now()
        datetime.timedelta(
            days=int(self.days.value or 0),
            hours=int(self.hours.value or 0),
            minutes=int(self.minutes.value or 0),
            seconds=int(self.seconds.value or 0)
        )
        then = now + datetime.timedelta(
            days=int(self.days.value or 0),
            hours=int(self.hours.value or 0),
            minutes=int(self.minutes.value or 0),
            seconds=int(self.seconds.value or 0)
        )
        # then = then.isoformat()
        self.member.muted(then)
