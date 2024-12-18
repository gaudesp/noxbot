import re
import string

class NewsFormatter:
  """Classe utilitaire pour le formatage de texte, nettoyage de contenu et gestion des émojis."""

  REPLACEMENTS = {
    r'\[img\].*?\[/img\]': '',                              # Supprime les images
    r'\[previewyoutube=.*?\]\s*?\[/previewyoutube\]': '',   # Supprime les vidéos
    r'\[(?!\*)[^]]*?\]': '',                                # Supprime les balises sauf [*]
    r'\[list\]|\[/*list\]': '',                             # Supprime les balises de liste
    r'\s*\[\*\](?=\S)': '\n- ',                             # Formate les éléments principaux en puces
    r'\s*\[\*\]\s*': '\n- ',                                # Remplace les sous-listes par des puces sans indentation
    r'・': '- ',                                            # Remplace les puces "・" par des tirets
    r'\n==\n+': '',                                         # Supprime "=="
    r'^\d+\.\s+': '',                                       # Supprime les numéros en début de ligne
    r'\n{3,}': '\n\n',                                      # Limite les retours à la ligne à 2 maximum
  }

  @staticmethod
  def clean_content(content: str, max_length: int = 500) -> str:
    """Nettoie et formate le contenu textuel brut avec un nombre de caractères maximum."""
    format_links = NewsFormatter._format_links(content)
    apply_replacements = NewsFormatter._apply_replacements(format_links)
    limit_length = NewsFormatter._limit_length(apply_replacements, max_length)
    cleaned_content = NewsFormatter._limit_lines(limit_length)
    if len(apply_replacements) > len(limit_length):
      cleaned_content = cleaned_content + "..."
    return cleaned_content

  @staticmethod
  def extract_image_urls(content: str) -> list[str]:
    """Extrait les URLs d'images uniquement des balises personnalisées `[img]`."""
    custom_image_urls = re.findall(r'\[img\](.+?)\[/img\]', content)
    image_urls = [
      url.replace('{STEAM_CLAN_IMAGE}', 'https://clan.akamai.steamstatic.com/images') for url in custom_image_urls
    ]
    return image_urls

  @staticmethod
  def _apply_replacements(text: str) -> str:
    """Applique les substitutions de texte pour nettoyer le contenu avec un format simplifié."""
    for pattern, repl in NewsFormatter.REPLACEMENTS.items():
      text = re.sub(pattern, repl, text, flags=re.MULTILINE)
    return text.strip()

  @staticmethod
  def _limit_length(text: str, max_length: int) -> str:
    """Tronque le texte à une longueur maximale."""
    if len(text) > max_length:
      return text[:max_length]
    return text

  @staticmethod
  def _limit_lines(text: str, max_lines: int = 10) -> str:
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
