# utils/logger.py
import logging
import datetime

class ConsoleColor:
    RED = "\033[31m"
    ORANGE = "\033[33m"
    GREEN = "\033[32m"
    BLUE = "\033[34m"
    WHITE = "\033[37m"
    RESET = "\033[0m"

class Logger:
  def __init__(self):
    self.logger = logging.getLogger("Logger")
    self.logger.setLevel(logging.DEBUG)

    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.DEBUG)

    formatter = logging.Formatter('%(message)s')
    console_handler.setFormatter(formatter)

    self.logger.addHandler(console_handler)

  def log(self, message, level="info"):
    if level == "error":
      color = ConsoleColor.RED
      level_name = "ERROR"
    elif level == "warning":
      color = ConsoleColor.ORANGE
      level_name = "WARNING"
    elif level == "success":
      color = ConsoleColor.GREEN
      level_name = "SUCCESS"
    else:
      color = ConsoleColor.BLUE
      level_name = "INFO"

    timestamp = self._get_timestamp()
    colored_message = f"{color}{timestamp} - {level_name} - {message}{ConsoleColor.RESET}"

    if level == "danger":
      self.logger.error(colored_message)
    elif level == "warning":
      self.logger.warning(colored_message)
    else:
      self.logger.info(colored_message)

  def _get_timestamp(self):
    return datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")

logger = Logger()
