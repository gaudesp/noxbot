# src/utils/helper.py
import re
import logging
from bs4 import BeautifulSoup
from os.path import dirname, abspath, join

root_directory = dirname(dirname(abspath(__file__)))

def set_commands_description(cogs, translator):
  """Définit la description des commandes pour chaque cog."""
  for cog in cogs:
    commands = cog.get_app_commands()
    for command in commands:
      description_key = f"cogs.{cog.qualified_name[:-3].lower()}.commands.{command.name}.description"
      command.description = translator.translate(description_key)

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

def clean_news_content(contents: str) -> str:
  """Nettoie le contenu des nouvelles en retirant le HTML et les balises non désirées."""
  soup = BeautifulSoup(contents, 'html.parser')
  cleaned_contents = soup.get_text(separator=' ', strip=True)
  cleaned_contents = re.sub(r'\[img\].*?\[/img\]', '', cleaned_contents)
  cleaned_contents = re.sub(r'\[previewyoutube=.*?\]\s*?\[/previewyoutube\]', '', cleaned_contents)
  cleaned_contents = re.sub(r'\[.*?\]', '', cleaned_contents)
  cleaned_contents = re.sub(r'\s+', ' ', cleaned_contents).strip()
  cleaned_contents = re.sub(r'^\d+\.\s*', '', cleaned_contents, flags=re.MULTILINE)
  return cleaned_contents 

def extract_image_urls(contents: str) -> list[str]:
  """Extrait les URL d'images à partir du contenu, y compris les balises img et les balises personnalisées."""
  soup = BeautifulSoup(contents, 'html.parser')
  image_urls = [img['src'] for img in soup.find_all('img')]
  custom_image_urls = re.findall(r'\[img\](.+?)\[/img\]', contents)
  image_urls += [url.replace('{STEAM_CLAN_IMAGE}', 'https://clan.akamai.steamstatic.com/images') for url in custom_image_urls]
  return image_urls
