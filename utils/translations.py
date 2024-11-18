import os
import json
from typing import Optional

from .dotenv import setting

class Translator:
  """Classe utilitaire pour gérer les traductions dans différentes langues."""

  def __init__(self, locales_path: str = 'locales', default_locale: str = 'en') -> None:
    """
    Initialise le gestionnaire de traductions.

    :param locales_path: Le chemin vers le répertoire contenant les fichiers de traduction (par défaut 'locales').
    :param default_locale: La locale par défaut à utiliser pour les traductions (par défaut 'en').
    :return: Aucun retour.
    """
    self.locales_path: str = locales_path
    self.default_locale: str = default_locale
    self.translations: dict[str, dict[str, str]] = self._load_translations()

  # Public methods

  def translate(self, message_id: str, locale: Optional[str] = None, **kwargs) -> str:
    """
    Traduit un message en fonction de son identifiant et de la locale spécifiée.

    :param message_id: Identifiant du message à traduire, sous forme de chaîne (par exemple 'greeting.hello').
    :param locale: Locale à utiliser pour la traduction. Si None, la locale par défaut est utilisée (par défaut 'en').
    :param kwargs: Arguments de formatage pour la traduction (ex. des variables à insérer dans le message).
    :return: Le message traduit si l'identifiant est trouvé, sinon retourne l'identifiant du message.
    :rtype: str
    """
    locale = locale or self.default_locale
    message = self._get_translation(locale)
    if message:
      translated_message = self._find_message(message_id, message)
      if translated_message:
        return translated_message.format(**kwargs)
    return message_id

  def get_locales(self) -> list[str]:
    """
    Retourne la liste des locales disponibles.

    :return: Liste des locales disponibles (ex. ['en', 'fr']).
    :rtype: list[str]
    """
    return list(self.translations.keys())

  # Private methods

  def _load_translations(self) -> dict[str, dict[str, str]]:
    """
    Charge toutes les traductions disponibles à partir des fichiers JSON dans le répertoire des locales.

    :return: Dictionnaire où les clés sont les locales (ex. 'en', 'fr') et les valeurs sont des dictionnaires 
             associant des identifiants de messages à leurs traductions respectives.
    :rtype: dict[str, dict[str, str]]
    """
    return {self._extract_locale(filename): self._load_translation_file(filename)
            for filename in self._get_locale_files()}

  def _get_locale_files(self) -> list[str]:
    """
    Retourne la liste des fichiers de traduction présents dans le répertoire des locales.

    :return: Liste des noms de fichiers de traduction (ex. ['en.json', 'fr.json']).
    :rtype: list[str]
    """
    return [f for f in os.listdir(self.locales_path) if f.endswith('.json')]

  def _extract_locale(self, filename: str) -> str:
    """
    Extrait la locale d'un nom de fichier en supprimant l'extension .json.

    :param filename: Le nom du fichier de traduction (par exemple 'en.json', 'fr.json').
    :return: La locale extraite du nom du fichier (par exemple 'en', 'fr').
    :rtype: str
    """
    return filename[:-5]

  def _load_translation_file(self, filename: str) -> dict[str, str]:
    """
    Charge un fichier de traduction au format JSON dans un dictionnaire.

    :param filename: Le nom du fichier de traduction à charger (par exemple 'en.json').
    :return: Dictionnaire représentant les traductions contenues dans ce fichier de traduction.
    :rtype: dict[str, str]
    """
    with open(os.path.join(self.locales_path, filename), 'r', encoding='utf-8') as file:
      return json.load(file)

  def _get_translation(self, locale: str) -> Optional[dict[str, str]]:
    """
    Récupère les traductions d'une locale spécifiée.

    :param locale: La locale pour laquelle récupérer les traductions (ex. 'en', 'fr').
    :return: Dictionnaire des traductions pour cette locale, ou None si aucune traduction n'est trouvée.
    :rtype: Optional[dict[str, str]]
    """
    return self.translations.get(locale)

  def _find_message(self, message_id: str, message: dict[str, str]) -> Optional[str]:
    """
    Recherche un message dans un dictionnaire de traductions en suivant l'identifiant.

    :param message_id: L'identifiant du message à rechercher (par exemple 'greeting.hello').
    :param message: Le dictionnaire des traductions pour la locale.
    :return: Le message correspondant à l'identifiant, ou None si l'identifiant n'existe pas.
    :rtype: Optional[str]
    """
    for key in message_id.split('.'):
      message = message.get(key)
      if message is None:
        return None
    return message

translator = Translator(locales_path=setting.get_locales_path(), default_locale=setting.get_default_locale())
