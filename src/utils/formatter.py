import re
from bs4 import BeautifulSoup

class NewsFormatter:
  """Classe utilitaire pour le formatage de texte, nettoyage de contenu et gestion des émojis."""

  EMOJI_PATTERN = re.compile(
    "[\U0001F600-\U0001F64F"
    "\U0001F300-\U0001F5FF"
    "\U0001F680-\U0001F6FF"
    "\U0001F1E0-\U0001F1FF"
    "\U00002702-\U000027B0"
    "\U000024C2-\U0001F251]+", flags=re.UNICODE
  )

  # Public methods

  @staticmethod
  def clean_content(content: str, max_length: int = 300) -> str:
    strip_html = NewsFormatter._strip_html(content)
    apply_replacements = NewsFormatter._apply_replacements(strip_html)
    truncate = NewsFormatter._truncate(apply_replacements, max_length)
    limit_lines = NewsFormatter._limit_lines(truncate)
    cleaned_content = NewsFormatter._finale_truncate(limit_lines)
    return cleaned_content

  @staticmethod
  def extract_image_urls(content: str) -> list[str]:
    """Extrait les URLs d'images des balises HTML et balises personnalisées `[img]`."""
    soup = BeautifulSoup(content, 'html.parser')
    image_urls = [img['src'] for img in soup.find_all('img')]
    custom_image_urls = re.findall(r'\[img\](.+?)\[/img\]', content)
    image_urls.extend(
      url.replace('{STEAM_CLAN_IMAGE}', 'https://clan.akamai.steamstatic.com/images') for url in custom_image_urls
    )
    return image_urls

  @staticmethod
  def isolate_emojis(text: str) -> tuple[str, dict]:
    """Remplace les émojis par des placeholders uniques et retourne un dictionnaire de correspondance."""
    emojis = {}
    cleaned_text = NewsFormatter.EMOJI_PATTERN.sub(lambda m: NewsFormatter._replace_with_placeholder(m, emojis), text)
    return cleaned_text, emojis

  @staticmethod
  def restore_emojis(text: str, emojis: dict) -> str:
    """Restaure les émojis en remplaçant les placeholders par les émojis d'origine."""
    for placeholder, emoji in emojis.items():
      text = text.replace(placeholder, emoji)
    return text

  # Private methods

  @staticmethod
  def _strip_html(content: str) -> str:
    """Extrait le texte d'un contenu HTML avec séparation par lignes."""
    soup = BeautifulSoup(content, 'html.parser')
    return soup.get_text(separator='\n', strip=True)

  @staticmethod
  def _apply_replacements(text: str) -> str:
    """Applique les substitutions de texte pour nettoyer le contenu, sans sous-listes."""
    replacements = {
      r'\[img\].*?\[/img\]': '',                              # Supprime les images
      r'\[previewyoutube=.*?\]\s*?\[/previewyoutube\]': '',   # Supprime les vidéos
      r'\[(?!list|[*])[^]]*?\]': '',                          # Supprime les balises sauf [list] et [*]
      r'\[list\]|\[/*list\]': '',                             # Supprime les balises de liste
      r'\s*\[\*\](?=\S)': '\n- ',                             # Formate les éléments principaux en puces
      r'\s*\[\*\]\s*': '\n- ',                                # Remplace les sous-listes par des puces sans indentation
      r'・': '- ',                                            # Remplace les puces "・" par des tirets
      r'\n==\n+': '',                                         # Supprime "=="
      r'^\d+\.\s+': '',                                       # Supprime les numéros en début de ligne
      r'\n{3,}': '\n\n'                                       # Limite les retours à la ligne à 2 maximum
    }
    for pattern, repl in replacements.items():
      text = re.sub(pattern, repl, text, flags=re.MULTILINE)
    return text

  @staticmethod
  def _truncate(text: str, max_length: int) -> str:
    """Tronque le texte à une longueur maximale"""
    if len(text) > max_length:
      return text[:max_length - 3].strip() + '...'
    return text

  @staticmethod
  def _replace_with_placeholder(match, emojis: dict) -> str:
    """Remplace un emoji par un placeholder unique basé sur son index."""
    emoji = match.group(0)
    placeholder = f"__EMOJI_{len(emojis)}__"
    emojis[placeholder] = emoji
    return placeholder

  @staticmethod
  def _limit_lines(text: str, max_lines: int = 7) -> str:
    """Limite le texte à un nombre maximum de lignes."""
    lines = text.splitlines()
    return "\n".join(lines[:max_lines])

  @staticmethod
  def _finale_truncate(text: str, min_length: int = 20) -> str:
    """Vérifie la longueur de la dernière phrase et tronque si nécessaire."""
    lines = text.strip().splitlines()
    last_line = lines[-1].strip() if lines else ''
    if len(last_line) < min_length:
      return '\n'.join(lines[:-1]).strip()
    return text.strip()
