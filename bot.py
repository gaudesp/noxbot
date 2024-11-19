from config.setting import setting
from utils.discord import bot
from utils.logging import logger

log = logger.get_logger('bot')

if __name__ == "__main__":
  log.info('Starting BOT...')
  bot.run(
    setting.discord_token,
    log_handler=None
  )
  log.info('BOT has been closed!')
