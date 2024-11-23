from datetime import datetime
import re
import string

class SteamFormatter:
  """Classe utilitaire pour le formatage de texte, nettoyage de contenu et gestion des émojis."""

  REPLACEMENTS = {
    r'\[img\].*?\[/img\]': '',                              # Supprime les images
    r'\[previewyoutube=.*?\]\s*?\[/previewyoutube\]': '',   # Supprime les vidéos
    r'\[(?!\*)[^]]*?\]': '',                                # Supprime les balises sauf [*]
    r'\[list\]|\[/*list\]': '',                             # Supprime les balises de liste
    r'\s*\[\*\](?=\S)': '\n- ',                             # Formate les éléments principaux en puces
    r'\s*\[\*\]\s*': '\n- ',                                # Remplace les sous-listes par des puces sans indentation
    r'^\d+\.\s+': '',                                       # Supprime les numéros en début de ligne
    r'[\n\s]{3,}': '\n\n',                                  # Remplace les lignes vides multiples par une seule ligne vide
  }

  @staticmethod
  def clean_content(content: str, max_length: int = 500) -> str:
    """Nettoie et formate le contenu textuel brut avec un nombre de caractères maximum."""
    format_links = SteamFormatter._format_links(content)
    apply_replacements = SteamFormatter._apply_replacements(format_links)
    limit_length = SteamFormatter._limit_length(apply_replacements, max_length)
    limit_lines = SteamFormatter._limit_lines(limit_length)
    cleaned_content = limit_lines
    if len(apply_replacements) > len(cleaned_content):
      cleaned_content = cleaned_content + "\n..."
    return cleaned_content
  
  @staticmethod
  def clean_date(timestamp: datetime):
    return datetime.fromtimestamp(timestamp)

  @staticmethod
  def extract_image(content: str) -> list[str]:
    custom_image_urls = re.findall(r'\[img\](.+?)\[/img\]', content)
    image_urls = [url.replace('{STEAM_CLAN_IMAGE}', 'https://clan.akamai.steamstatic.com/images') for url in custom_image_urls]
    return image_urls.pop(0) if image_urls else None

  @staticmethod
  def _apply_replacements(text: str) -> str:
    """Applique les substitutions de texte pour nettoyer le contenu avec un format simplifié."""
    for pattern, repl in SteamFormatter.REPLACEMENTS.items():
      text = re.sub(pattern, repl, text, flags=re.MULTILINE)
    return text.strip()

  @staticmethod
  def _limit_length(text: str, max_length: int) -> str:
    """Tronque le texte à une longueur maximale."""
    if len(text) > max_length:
      truncated = text[:max_length].rstrip(' \n')
      return truncated + "..."
    return text

  @staticmethod
  def _limit_lines(text: str, max_lines: int = 11) -> str:
    """Limite le texte à un nombre maximum de lignes."""
    lines = text.splitlines()
    return "\n".join(lines[:max_lines])

  @staticmethod
  def _format_links(content: str) -> str:
    """Extrait les liens et remplace les balises de lien par un format simple."""
    content = re.sub(
      r'\[url=(.+?)\](.+?)\[/url\]', 
      lambda m: re.sub(f'[{re.escape(string.punctuation)}]', '', m.group(2)).replace(':', '') + ": " + m.group(1), 
      content
    )
    return content
