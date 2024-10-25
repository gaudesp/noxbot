# config/settings.py
import os
from dotenv import load_dotenv

class Settings:
  def __init__(self) -> None:
    """Charge les variables d'environnement et initialise les paramètres de configuration."""
    load_dotenv()
    self.bot_name = 'NoxBot'  # Nom du bot
    self.check_interval = int(os.getenv('CHECK_INTERVAL'))  # Intervalle de vérification en secondes
    self.db_path = 'sqlite+aiosqlite:///config/database.db'  # Chemin vers la base de données SQLite
    self.steam_api_key = os.getenv("STEAM_API_KEY")  # Clé API pour Steam
    self.discord_token = os.getenv("DISCORD_TOKEN")  # Jeton d'authentification pour Discord
    self.discord_app_id = os.getenv("DISCORD_APP_ID")  # ID de l'application Discord
