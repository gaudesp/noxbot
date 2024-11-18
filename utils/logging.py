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
    self.log_format: str = log_format or "[{asctime}] [{levelname}] {name} {message}"
    self.date_format: str = date_format or "%Y-%m-%d %H:%M:%S"
    self.log_file: Optional[str] = log_file

    self._basic_formatter: logging.Formatter = self._create_basic_formatter()
    self._colored_formatter: logging.Formatter = self._create_colored_formatter()
    self._file_handler: logging.FileHandler = self._create_file_handler()
    self._stream_handler: logging.StreamHandler = self._create_stream_handler()

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
    logger.addHandler(self._stream_handler)
    if self._file_handler:
        logger.addHandler(self._file_handler)
    return logger
  
  # Private methods

  def _create_basic_formatter(self) -> logging.Formatter:
    """
    Crée le formatteur de logs.

    :return: Instance de logging.Formatter configurée.
    :rtype: logging.Formatter
    """
    return logging.Formatter(fmt=self.log_format, datefmt=self.date_format, style="{")
      
  def _create_colored_formatter(self) -> logging.Formatter:
      """Crée un formatteur avec des couleurs pour la console."""
      COLORS = {
          'DEBUG': '\033[94m',   # Bleu
          'INFO': '\033[32m',    # Vert
          'WARNING': '\033[33m', # Jaune
          'ERROR': '\033[31m',   # Rouge
          'CRITICAL': '\033[41m',# Fond rouge
          'DEFAULT': '\033[97m', # Blanc
          'GREY': '\033[90m', # Gris
          'VIOLET': '\033[35m',  # Violet\033[90m
      }
      RESET = '\033[0m'  # Réinitialisation des couleurs

      # Formattage avec les couleurs appliquées dynamiquement en fonction du levelname
      LOG_FORMAT = (
          f"{COLORS['GREY']}{{asctime}}{RESET} "  # asctime en gris
          f"{{levelname}} "  # Pas de couleur directement, on la gère dynamiquement
          f"{COLORS['VIOLET']}{{name}}{RESET} "  # name en violet
          f"{COLORS['DEFAULT']}{{message}}{RESET}"  # message en blanc
      )

      # Appliquer la couleur en fonction du niveau de log dans un processus de substitution
      class ColoredFormatter(logging.Formatter):
          def format(self, record):
              log_message = super().format(record)
              levelname_color = COLORS.get(record.levelname, COLORS['DEFAULT'])
              return log_message.replace(record.levelname, f"{levelname_color}{record.levelname}{RESET}")

      return ColoredFormatter(fmt=LOG_FORMAT, datefmt=self.date_format, style='{')

  def _create_stream_handler(self) -> logging.StreamHandler:
    """
    Crée un gestionnaire pour afficher les logs dans la console.

    :return: Instance de logging.StreamHandler configurée.
    :rtype: logging.StreamHandler
    """
    self._stream_handler = logging.StreamHandler()
    self._stream_handler.setLevel(self.console_level)
    self._stream_handler.setFormatter(self._colored_formatter)
    return self._stream_handler

  def _create_file_handler(self) -> Optional[logging.FileHandler]:
    """
    Crée un gestionnaire pour écrire les logs dans un fichier.

    :return: Instance de logging.FileHandler configurée, ou None si aucun fichier n'est spécifié.
    :rtype: Optional[logging.FileHandler]
    """
    if not self.log_file:
      return None
    self._file_handler = logging.FileHandler(self.log_file, encoding="utf-8", mode="w")
    self._file_handler.setLevel(self.file_level)
    self._file_handler.setFormatter(self._basic_formatter)
    return self._file_handler

logger = Logger(log_file=setting.get_log_file())
