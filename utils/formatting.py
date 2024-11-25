from datetime import datetime
from PIL import Image
from io import BytesIO
import re
import string

import requests
from utils.logging import logger

log = logger.get_logger(__name__)

class SteamFormatter:
  """Classe utilitaire pour le formatage de texte, nettoyage de contenu et gestion des émojis."""

  REPLACEMENTS = {
    r'\[b\](.*?)(?=\[/?b\]|$)': r'\1', # Supprime les balises [b]
    r'\[u\](.*?)(?=\[/?u\]|$)': r'\1', # Supprime les balises [u]
    r'\[i\](.*?)(?=\[/?i\]|$)': r'\1', # Supprime les balises [i]
    r'\[strike\](.*?)(?=\[/?strike\]|$)': r'\1', # Supprime les balises [strike]
    r'\[url=[^\]]+\]\[img.*?\].*?\[/img\]\[/url\]': '', # Supprime les balises [url] qui contiennent une image à l'intérieur
    r'\[url=([^\]]+)\](?!.*\[img.*?\])(.*?)\[/url\]': lambda m: re.sub(f'[{re.escape(string.punctuation)}]', '', m.group(2)).replace(':', '') + ": " + m.group(1), # Supprime les balises [url] qui ne contiennent pas d'image et formate le texte
    r'\[img\].*?\[/img\]': '', # Supprime les images
    r'\[previewyoutube=.*?\]\s*?\[/previewyoutube\]': '', # Supprime les vidéos
    r'\[list\]|\[/*list\]': '', # Supprime les balises de liste
    r'・([^ ]+)': r'- \1', # Remplace "・" par "-"
    r'\s*\[\*\](?=\S)': '\n- ', # Convertit les éléments principaux en puces
    r'\s*\[\*\]\s*': '\n- ', # Corrige les sous-listes en puces
    r'((?:\[h[1-6]\].*?\[/h[1-6]\]\s*)+)(.*)': lambda m: ' · '.join(re.sub(r'\[h[1-6]\](.*?)\[/h[1-6]\]', r'\1', m.group(1)).strip().split('\n')) + '\n' + m.group(2), # Formate les titres de type [h1] à [h6] en les joignant avec " · " et en conservant le texte du reste
    r'^\d+\.\s+': '\n- ', # Supprime les numéros en début de ligne
    r'[▼==]': '', # Supprime les caractères ▼ et ==
    r'^.*⤷.*\n': '', # Supprime les lignes contenant ⤷
    r'\[h[1-6]\]|\[\/h[1-6]\]': '', # Supprime les balises de titre [h1] à [h6]
    r'^\s*\[\s*(.*?)\s*\]*(?=\n- )': r'\1', # Convertit les balises [] en titres si suivi d'une liste
    r'\[.*?\]': '', # Supprime les autres balises [xxx] restantes
    r'^\s*#+\s*\n*(.*?)\n*#+\s*$': r'\n\1', # Supprime les symboles de titre (comme ####) et garde uniquement le texte entre les symboles
    r'(?<=\S)\n{2,}(?=\s*-)': '\n', # Supprime les sauts de ligne multiples avant un élément de liste
    r'^(?!- )(.*?)(?=\n- )': lambda match: f"**{match.group(1).title()}**" if match.group(1).strip() else match.group(1), # Formate les titres en gras
    r'^[\s]+\n': '\n', # Supprime les lignes vides en début de texte
    r'[\n]{2,}': '\n\n', # Réduit les sauts de ligne multiples à un seul
    ' {2,}': ' ', # Réduit les espaces multiples à un seul
    r'(\S.*\S)\n\*\*': r'\1\n\n**', # Assure qu'un titre en gras soit suivi d'un saut de ligne avant un autre titre
    r'[\[\]]': '', # Supprime tous les crochets restants
    r'^(?!\*\*)([^\n]{2,30})(?=\n(?!\s*[\n-*]))': r'**\1**', # Met en gras les titres restants
  }

  @staticmethod
  def clean_content(content: str, max_length: int = 500) -> str:
    """Nettoie et formate le contenu textuel brut avec un nombre de caractères maximum."""
    log.debug(f"Input : \"{content}\"")
    apply_replacements = SteamFormatter._apply_replacements(content)
    limit_length = SteamFormatter._limit_length(apply_replacements, max_length)
    limit_lines = SteamFormatter._limit_lines(limit_length)
    cleaned_content = SteamFormatter._filter_lastline(limit_lines)
    if len(apply_replacements) > len(cleaned_content):
      cleaned_content = cleaned_content + "\n..."
    log.debug(f"Output : \"{cleaned_content}\"")
    return cleaned_content
  
  @staticmethod
  def clean_date(timestamp: datetime):
    """Convertit un timestamp en objet datetime."""
    return datetime.fromtimestamp(timestamp)
  
  @staticmethod
  def extract_image(content: str, min_width: int = 460, min_height: int = 215) -> str:
    """Récupère la première image valide non GIF avec dimensions minimales."""
    content_without_url = re.sub(r'\[url=.*?\].*?\[/url\]', '', content, flags=re.DOTALL)
    custom_image_urls = re.findall(r'\[img\](.+?)\[/img\]', content_without_url)
    for url in custom_image_urls:
      if url.lower().endswith('.gif'):
        continue
      url = url.replace('{STEAM_CLAN_IMAGE}', 'https://clan.akamai.steamstatic.com/images')
      try:
        response = requests.get(url, timeout=5)
        response.raise_for_status()
        img = Image.open(BytesIO(response.content))
        if img.width >= min_width and img.height >= min_height:
          return url
      except Exception:
        continue
    return None

  @staticmethod
  def _apply_replacements(text: str) -> str:
    """Applique les remplacements définis dans REPLACEMENTS."""
    for pattern, repl in SteamFormatter.REPLACEMENTS.items():
      text = re.sub(pattern, repl, text, flags=re.MULTILINE)
    return text.strip()

  @staticmethod
  def _limit_lines(text: str, max_lines: int = 12) -> str:
    """Limite le texte à un nombre maximum de lignes."""
    lines = text.splitlines()
    return "\n".join(lines[:max_lines])

  @staticmethod
  def _limit_length(text: str, max_length: int) -> str:
      """ Tronque le texte à une longueur maximale."""
      if len(text) > max_length:
        truncated = text[:max_length].rstrip(' \n')
        if re.search(r'https?://\S+', truncated.splitlines()[-1]):
          truncated = ('\n'.join(truncated.splitlines()[:-1])).strip()
        else:
          truncated = truncated + ".."
        return truncated
      return text
  
  @staticmethod
  def _filter_lastline(content: str) -> str:
    """Supprime une dernière ligne incomplète ou mal formattée."""
    lines = content.splitlines()
    if lines and lines[-1].startswith('**'):
      lines = lines[:-1]
    return '\n'.join(lines).strip()
