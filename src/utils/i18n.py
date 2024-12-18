# src/utils/i18n.py
import os
import json
from typing import Dict
from src.services.guild import GuildService

class I18n:
  def __init__(self, bot):
    """Initialise le traducteur avec le chemin des fichiers de traductions."""
    self.locales_path = 'src/locales'
    self.translations = self.load_translations()
    self.guild_service = GuildService(bot)
    self.default_locale = 'en'

  def load_translations(self) -> Dict[str, Dict[str, str]]:
    """Charge toutes les traductions disponibles à partir des fichiers de langue."""
    return {
      self.extract_locale(filename): self.load_translation_file(filename)
      for filename in self.get_locale_files()
    }

  def get_locale_files(self) -> list[str]:
    """Retourne une liste des fichiers de langue disponibles dans le répertoire spécifié."""
    return [f for f in os.listdir(self.locales_path) if f.endswith('.json')]
  
  def get_locales(self) -> list[str]:
    """Retourne la liste des locales disponibles."""
    return list(self.translations.keys())

  def extract_locale(self, filename: str) -> str:
    """Extrait la locale d'un nom de fichier en supprimant l'extension."""
    return filename[:-5]

  def load_translation_file(self, filename: str) -> Dict[str, str]:
    """Charge le contenu d'un fichier de traduction JSON."""
    with open(os.path.join(self.locales_path, filename), 'r', encoding='utf-8') as f:
      return json.load(f)

  def find_message(self, message_id: str, message: Dict) -> str:
    """Recherche un message dans un dictionnaire en utilisant un identifiant de message."""
    for key in message_id.split('.'):
      message = message.get(key)
      if message is None:
        return None
    return message

  def translate(self, message_id: str, locale: str = None, **kwargs) -> str:
    """Traduit un message en fonction de l'identifiant et de la locale spécifiée."""
    locale = locale or self.default_locale
    message = self.translations.get(locale)
    if not message:
      return message_id
    found_message = self.find_message(message_id, message)
    return found_message.format(**kwargs) if isinstance(found_message, str) else found_message or message_id
