import logging
from typing import Optional
from config import config

COLORS = {
  'DEBUG': '\033[94m',
  'INFO': '\033[32m',
  'WARNING': '\033[33m',
  'ERROR': '\033[31m',
  'CRITICAL': '\033[41m',
  'DEFAULT': '\033[97m',
  'GREY': '\033[90m',
  'VIOLET': '\033[35m',
}
RESET = '\033[0m'

LOG_FORMAT = (
  f"{COLORS['GREY']}{{asctime}}{RESET} "
  f"{{levelname}} "
  f"{COLORS['VIOLET']}{{name}}{RESET} "
  f"{COLORS['DEFAULT']}{{message}}{RESET}"
)

class ColoredFormatter(logging.Formatter):
  def format(self, record):
    log_message = super().format(record)
    levelname_color = COLORS.get(record.levelname, COLORS['DEFAULT'])
    return log_message.replace(record.levelname, f"{levelname_color}{record.levelname}{RESET}")

class Logger(logging.Logger):
  def __init__(
    self,
    file_level: int = logging.DEBUG,
    console_level: int = logging.INFO,
    log_format: Optional[str] = None,
    date_format: Optional[str] = None,
    log_file: Optional[str] = None
  ) -> None:
    self.file_level: int = file_level
    self.console_level: int = console_level
    self.log_format: str = log_format or "[{asctime}] [{levelname}] {name} {message}"
    self.date_format: str = date_format or "%Y-%m-%d %H:%M:%S"
    self.log_file: Optional[str] = log_file
    self._basic_formatter: logging.Formatter = self._create_basic_formatter()
    self._colored_formatter: logging.Formatter = self._create_colored_formatter()
    self._file_handler: logging.FileHandler = self._create_file_handler()
    self._stream_handler: logging.StreamHandler = self._create_stream_handler()

  def get_logger(self, name: str) -> logging.Logger:
    logger = logging.getLogger(name)
    logger.setLevel(logging.DEBUG)
    logger.addHandler(self._stream_handler)
    if self._file_handler:
        logger.addHandler(self._file_handler)
    return logger
  
  def _create_basic_formatter(self) -> logging.Formatter:
    return logging.Formatter(fmt=self.log_format, datefmt=self.date_format, style="{")
      
  def _create_colored_formatter(self) -> ColoredFormatter:
    return ColoredFormatter(fmt=LOG_FORMAT, datefmt=self.date_format, style='{')

  def _create_stream_handler(self) -> logging.StreamHandler:
    self._stream_handler = logging.StreamHandler()
    self._stream_handler.setLevel(self.console_level)
    self._stream_handler.setFormatter(self._colored_formatter)
    return self._stream_handler

  def _create_file_handler(self) -> Optional[logging.FileHandler]:
    if not self.log_file:
      return None
    self._file_handler = logging.FileHandler(self.log_file, encoding="utf-8", mode="w")
    self._file_handler.setLevel(self.file_level)
    self._file_handler.setFormatter(self._basic_formatter)
    return self._file_handler

logger = Logger(log_file=config.log_file)
