import os
from pathlib import Path
from typing import Optional
from dotenv import load_dotenv

class Setting:
  """Classe utilitaire pour gérer les paramètres d'application via les variables d'environnement."""

  def __init__(self) -> None:
    """
    Initialise les paramètres à partir des variables d'environnement.
    """
    load_dotenv(dotenv_path=Path('config') / '.env')

    self.discord_token: str = self._get_env_var('DISCORD_TOKEN')
    self.db_path: str = self._get_env_var('DB_PATH')
    self.log_file: Optional[str] = self._get_env_var('LOG_FILE')
    self.locales_path: str = self._get_env_var('LOCALES_PATH', 'locales')
    self.default_locale: str = self._get_env_var('DEFAULT_LOCALE', 'en')
    self.discord_owner_id: str = self._get_env_var('DISCORD_OWNER_ID')

  # Private methods

  def _get_env_var(self, var_name: str, default: Optional[str] = None) -> Optional[str]:
    """
    Récupère la valeur d'une variable d'environnement, avec une valeur par défaut optionnelle.

    :param var_name: Le nom de la variable d'environnement.
    :type var_name: str
    :param default: La valeur par défaut à utiliser si la variable n'est pas définie.
    :type default: Optional[str]
    :return: La valeur de la variable d'environnement ou la valeur par défaut.
    :rtype: Optional[str]
    """
    return os.getenv(var_name, default)

setting = Setting()
