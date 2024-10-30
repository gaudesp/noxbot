# src/utils/helper.py
import re
import logging
from bs4 import BeautifulSoup
from os.path import dirname, abspath, join
from src.utils.i18n import I18n

root_directory = dirname(dirname(abspath(__file__)))

def set_commands_description(cogs, i18n: I18n):
  """Définit la description des commandes pour chaque cog."""
  for cog in cogs:
    commands = cog.get_app_commands()
    for command in commands:
      description_key = f"cogs.{cog.qualified_name[:-3].lower()}.commands.{command.name}.description"
      command.description = i18n.translate(description_key)

def set_logging(file_level: int = logging.DEBUG, console_level: int = logging.INFO, filename: str = "../discord.log") -> tuple[logging.Logger, logging.StreamHandler]:
  """Configure le système de journalisation avec des gestionnaires de fichier et de console."""
  logger = logging.getLogger("discord")
  logger.setLevel(logging.DEBUG)
  log_formatter = logging.Formatter(fmt="[{asctime}] [{levelname}] {name}: {message}", datefmt="%Y-%m-%d %H:%M:%S", style="{")

  file_handler = logging.FileHandler(filename=join(root_directory, filename), encoding="utf-8", mode='w')
  file_handler.setFormatter(log_formatter)
  file_handler.setLevel(file_level)
  logger.addHandler(file_handler)

  console_handler = logging.StreamHandler()
  console_handler.setFormatter(log_formatter)
  console_handler.setLevel(console_level)
  logger.addHandler(console_handler)

  return logger, console_handler
