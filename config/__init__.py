import os
from typing import Optional
from dotenv import load_dotenv

class Config:
  def __init__(self) -> None:
    load_dotenv()

    self.discord_token: str = self._get_env_var('DISCORD_TOKEN')
    self.db_path: str = self._get_env_var('DB_PATH')
    self.log_file: Optional[str] = self._get_env_var('LOG_FILE')
    self.locales_path: str = self._get_env_var('LOCALES_PATH', 'locales')
    self.default_locale: str = self._get_env_var('DEFAULT_LOCALE', 'en')
    self.discord_owner_id: str = self._get_env_var('DISCORD_OWNER_ID')

  def _get_env_var(self, var_name: str, default: Optional[str] = None) -> Optional[str]:
    return os.getenv(var_name, default)

config = Config()
