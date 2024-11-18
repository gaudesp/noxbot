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

  # Public methods

  def get_discord_token(self) -> str:
    """
    Retourne le token Discord.

    :return: Le token Discord.
    :rtype: str
    """
    return self.discord_token

  def get_db_path(self) -> str:
    """
    Retourne le chemin vers la base de données.

    :return: Le chemin vers la base de données.
    :rtype: str
    """
    return self.db_path

  def get_log_file(self) -> Optional[str]:
    """
    Retourne le chemin vers le fichier de log.

    :return: Le chemin du fichier de log ou None.
    :rtype: Optional[str]
    """
    return self.log_file

  def get_locales_path(self) -> str:
    """
    Retourne le chemin vers le répertoire des locales.

    :return: Le chemin des locales.
    :rtype: str
    """
    return self.locales_path

  def get_default_locale(self) -> str:
    """
    Retourne la locale par défaut.

    :return: La locale par défaut.
    :rtype: str
    """
    return self.default_locale

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
