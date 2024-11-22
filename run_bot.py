from config.setting import setting
from utils.discord import bot
from utils.logging import logger
from models import Game, FollowedGame, News, Server, Subscription, User

log = logger.get_logger(__name__)

if __name__ == "__main__":
  log.info('Starting BOT...')
  bot.run(
    setting.discord_token,
    log_handler=None
  )
  log.info('BOT has been closed!')
