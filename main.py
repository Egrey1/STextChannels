import config
import dependencies as deps

async def load_extensions():
    await deps.bot.load_extension('basic_commands')

async def on_ready():
    await load_extensions()
    print(f'Бот {deps.bot.user} успешно запущен!')

if __name__ == "__main__":
    config.firstConfig() 
    deps.bot.event(on_ready) 
    deps.bot.run(deps.TOKEN) 