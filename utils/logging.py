import logging
from typing import Optional

from .dotenv import setting

class Logger:
  """Classe utilitaire pour configurer des loggers génériques et réutilisables."""

  def __init__(
    self,
    file_level: int = logging.DEBUG,
    console_level: int = logging.INFO,
    log_format: Optional[str] = None,
    date_format: Optional[str] = None,
    log_file: Optional[str] = None
  ) -> None:
    """
    Initialise la configuration par défaut pour les loggers.

    :param file_level: Niveau de log pour les fichiers (ex: DEBUG, INFO).
    :type file_level: int
    :param console_level: Niveau de log pour la console.
    :type console_level: int
    :param log_format: Format des messages de log.
    :type log_format: Optional[str]
    :param date_format: Format de la date des logs.
    :type date_format: Optional[str]
    :param log_file: Nom du fichier pour les logs.
    :type log_file: Optional[str]
    """
    self.file_level: int = file_level
    self.console_level: int = console_level
    self.log_format: str = log_format or "[{asctime}] [{levelname}] {name}: {message}"
    self.date_format: str = date_format or "%Y-%m-%d %H:%M:%S"
    self.log_file: Optional[str] = log_file
    self._formatter: logging.Formatter = self._create_formatter()

  # Public methods

  def get_logger(self, name: str) -> logging.Logger:
    """
    Retourne un logger configuré pour le module spécifié.

    :param name: Nom du logger (souvent __name__).
    :type name: str
    :return: Instance de logging.Logger configurée.
    :rtype: logging.Logger
    """
    logger = logging.getLogger(name)
    logger.setLevel(logging.DEBUG)

    # Ajout des gestionnaires uniquement si le logger n'en a pas déjà.
    if not logger.hasHandlers():
      logger.addHandler(self._create_console_handler())
      file_handler = self._create_file_handler()
      if file_handler:
        logger.addHandler(file_handler)
    return logger

  # Private methods

  def _create_formatter(self) -> logging.Formatter:
    """
    Crée le formatteur de logs.

    :return: Instance de logging.Formatter configurée.
    :rtype: logging.Formatter
    """
    return logging.Formatter(fmt=self.log_format, datefmt=self.date_format, style="{")

  def _create_console_handler(self) -> logging.StreamHandler:
    """
    Crée un gestionnaire pour afficher les logs dans la console.

    :return: Instance de logging.StreamHandler configurée.
    :rtype: logging.StreamHandler
    """
    console_handler = logging.StreamHandler()
    console_handler.setLevel(self.console_level)
    console_handler.setFormatter(self._formatter)
    return console_handler

  def _create_file_handler(self) -> Optional[logging.FileHandler]:
    """
    Crée un gestionnaire pour écrire les logs dans un fichier.

    :return: Instance de logging.FileHandler configurée, ou None si aucun fichier n'est spécifié.
    :rtype: Optional[logging.FileHandler]
    """
    if not self.log_file:
      return None
    file_handler = logging.FileHandler(self.log_file, encoding="utf-8", mode="a")
    file_handler.setLevel(self.file_level)
    file_handler.setFormatter(self._formatter)
    return file_handler

logger = Logger(log_file=setting.get_log_file())

