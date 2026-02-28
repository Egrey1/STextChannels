import config
import dependencies as deps
import logging

async def load_extensions():
    await deps.bot.load_extension('basic_commands')
    await deps.bot.load_extension('admin_commands')

async def on_ready():
    await load_extensions()
    await config.secondConfig()
    logging.info(f'Бот {deps.bot.user} успешно запущен!')

if __name__ == "__main__":
    config.firstConfig() 
    deps.bot.event(on_ready) 
    deps.bot.run(deps.TOKEN) 