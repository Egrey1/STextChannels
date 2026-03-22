from ..library import Modal, deps, TextInput, Interaction, randint, TextStyle

class ItemsModal(Modal):
    def __init__(self, guild_id: int):
        super().__init__(title='Добавление товара')
        
        self.name_ =         TextInput(
                                label='Наименование', 
                                placeholder='Имя товара', 
                                max_length=45, 
                                required=True)
        
        self.description_ =  TextInput(
                                label='Описание', 
                                placeholder='Описание товара', 
                                max_length=200, 
                                required=True,
                                style=TextStyle.paragraph)
        
        self.price_ =        TextInput(
                                label='Цена', 
                                placeholder='Цена товара', 
                                max_length=10, 
                                required=True)
        
        self.currency_ =      TextInput(
                                label='Валюта', 
                                placeholder='Пусто, для обычных кредитов, kk для красных',
                                max_length=2,
                                required=False)
        
        self.guild_id = guild_id

        self.add_item(self.name_)
        self.add_item(self.description_)
        self.add_item(self.price_)
        self.add_item(self.currency_)
    
    async def on_submit(self, interaction: Interaction):
        self.name = self.name_.value
        self.description = self.description_.value
        self.price = int(self.price_.value)
        self.currency = deps.CURRENCY.k if not self.currency_.value else deps.CURRENCY.kk

        if self.price < 0:
            await interaction.response.send_message('Цена не может быть отрицательной!', ephemeral=True)
            return
        
        new_id = randint(0, 1000000)
        i = deps.ShopItem(id_=new_id)

        while i.name:
            new_id = randint(0, 1000000)
            i = deps.ShopItem(id_=new_id)
        
        try:
            deps.ShopItem(self.name, new_id, self.description, self.price, self.guild_id, self.currency, True)
            await interaction.response.send_message('Товар успешно добавлен!', ephemeral=True)
        except Exception as e:
            await interaction.response.send_message(f'Произошла ошиибка при добавлении товара! Обратитесь к разработчику! `{e}`', ephemeral=True)


class EditItemModal(Modal):
    def __init__(self, item_id: int, guild_id: int):
        super().__init__(title='Изменение предмета')

        self.name_ =         TextInput(
                                label='Наименование', 
                                placeholder='Имя товара', 
                                max_length=45, 
                                required=False)
        
        self.description_ =  TextInput(
                                label='Описание', 
                                placeholder='Описание товара', 
                                max_length=200, 
                                required=False,
                                style=TextStyle.paragraph)
        
        self.price_ =        TextInput(
                                label='Цена', 
                                placeholder='Цена товара', 
                                max_length=10, 
                                required=False)
        
        self.currency_ =      TextInput(
                                label='Валюта', 
                                placeholder='Пусто, для обычных кредитов, kk для красных',
                                max_length=2,
                                required=False)
        
        self.guild_id = guild_id
        self.item_id = item_id

        self.add_item(self.name_)
        self.add_item(self.description_)
        self.add_item(self.price_)
        self.add_item(self.currency_)
        
    async def on_submit(self, interaction: Interaction):
        if not (self.name_.value or self.description_.value or self.price_.value):
            await interaction.response.send_message('Ты же ничего не изменил!', ephemeral=True)
        
        item = deps.ShopItem(id_=self.item_id)

        name = self.name_.value if self.name_.value else item.name
        description = self.description_.value if self.description_.value else item.description
        price = self.price_.value if self.price_.value else item.price
        self.currency = deps.CURRENCY.k if not self.currency_.value else deps.CURRENCY.kk

        deps.ShopItem(name, self.item_id, description, price, self.guild_id, self.currency, True)
        await interaction.response.send_message(f'Предмет {item.name}' + (f' ({self.name_.value})' if self.name_.value else '') + ' успешно изменен!')