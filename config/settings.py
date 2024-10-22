# config/settings.py
import os
from dotenv import load_dotenv

class Settings:
  def __init__(self) -> None:
    """Charge les paramètres de configuration depuis les variables d'environnement."""
    load_dotenv()
    self.check_interval = int(os.getenv('CHECK_INTERVAL', 3600))
    self.db_path = 'sqlite+aiosqlite:///config/database.db'
    self.steam_api_key = os.getenv("STEAM_API_KEY")
    self.discord_token = os.getenv("DISCORD_TOKEN")
    self.discord_app_id = os.getenv("DISCORD_APP_ID")
