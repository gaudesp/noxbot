# config/translator.py
import os
import json
from typing import Dict

class Translator:
  def __init__(self, locales_path: str):
    """Initialise la classe avec les fichiers JSON de traductions."""
    self.locales_path = locales_path
    self.translations = self.load_translations()
    self.default_locale = 'en'

  def load_translations(self) -> Dict[str, Dict[str, str]]:
    """Charge les traductions depuis les fichiers JSON."""
    return {
      self.extract_locale(filename): self.load_translation_file(filename)
      for filename in self.get_locale_files()
    }

  def get_locale_files(self) -> list[str]:
    """Retourne les fichiers de locale au format JSON."""
    return [f for f in os.listdir(self.locales_path) if f.endswith('.json')]

  def extract_locale(self, filename: str) -> str:
    """Extrait la locale d'un nom de fichier."""
    return filename[:-5]

  def load_translation_file(self, filename: str) -> Dict[str, str]:
    """Charge le contenu d'un fichier JSON de traduction."""
    with open(os.path.join(self.locales_path, filename), 'r', encoding='utf-8') as f:
      return json.load(f)

  def find_message(self, message_id: str, message: Dict) -> str:
    """Recherche la traduction en suivant les clés imbriquées."""
    for key in message_id.split('.'):
      message = message.get(key)
      if message is None:
        return None
    return message

  def translate(self, message_id: str, locale: str = None, **kwargs) -> str:
    """Retourne la traduction pour le message ID et la locale spécifiée."""
    locale = locale or self.default_locale
    message = self.translations.get(locale)
    if not message:
      return message_id 
    found_message = self.find_message(message_id, message)
    return found_message.format(**kwargs) if isinstance(found_message, str) else found_message or message_id

  def __call__(self, message_id: str, locale: str = None, **kwargs) -> str:
    """Permet d'appeler l'instance pour traduire un message."""
    return self.translate(message_id, locale, **kwargs)
