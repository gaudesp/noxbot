from datetime import datetime
import re
import string

class SteamFormatter:
  """Classe utilitaire pour le formatage de texte, nettoyage de contenu et gestion des émojis."""

  REPLACEMENTS = {
    r'\[img\].*?\[/img\]': '',  # Supprime les images standard
    r'img.*?{STEAM_CLAN_IMAGE}.*?jpg': '',  # Supprime les images Steam spécifiques
    r'\[url=.*?\].*?\[/url\]': '',  # Supprime les balises [url=][/url] et leur contenu
    r'\[previewyoutube=.*?\]\s*?\[/previewyoutube\]': '',  # Supprime les vidéos
    r'\[list\]|\[/*list\]': '',  # Supprime les balises de liste
    r'\s*\[\*\](?=\S)': '\n- ',  # Formate les éléments principaux en puces
    r'\s*\[\*\]\s*': '\n- ',  # Remplace les sous-listes par des puces sans indentation
    r'^\d+\.\s+': '',  # Supprime les numéros en début de ligne
    r'[▼==]': '',  # Supprime les caractères ▼ et ==
    r'・([^ ]+)': r'- \1',  # Remplace "・" par "-"
    r'^.*⤷.*\n': '',  # Supprime les lignes qui contiennent ⤷
    r'\[h[1-6]\]|\[\/h[1-6]\]': '',  # Supprime les balises [h1] à [h6]
    r'^\s*\[\s*(.*?)\s*\]\s*(?=\n- )': r'\1',  # Crée les titres de liste à partir des autres balises []
    r'\[.*?\]': '',  # Supprime les autres balises
    r'^(?!- )(.*?)(?=\n- )': lambda match: '**' + match.group(1).capitalize() + '**',  # Capitalize et met en gras les titres de liste
    r'[\n\s]{2,}': '\n',  # Remplace les lignes vides multiples par une seule
  }

  @staticmethod
  def clean_content(content: str, max_length: int = 1000) -> str:
    """Nettoie et formate le contenu textuel brut avec un nombre de caractères maximum."""
    print(f"Input : \"{content}\"")
    format_links = SteamFormatter._format_links(content)
    apply_replacements = SteamFormatter._apply_replacements(format_links)
    limit_length = SteamFormatter._limit_length(apply_replacements, max_length)
    limit_lines = SteamFormatter._limit_lines(limit_length)
    cleaned_content = SteamFormatter._filter_lastline(limit_lines)
    if len(apply_replacements) > len(cleaned_content):
      cleaned_content = cleaned_content + "\n..."
    print(f"-------------------------------------------------")
    print(f"Output : \"{cleaned_content}\"")
    return cleaned_content
  
  @staticmethod
  def clean_date(timestamp: datetime):
    return datetime.fromtimestamp(timestamp)

  @staticmethod
  def extract_image(content: str) -> str:
    """Récupère la première image qui n'est pas dans une balise [url]."""
    # Supprime les balises [url] et leur contenu
    content_without_url = re.sub(r'\[url=.*?\].*?\[/url\]', '', content, flags=re.DOTALL)
    # Trouve toutes les balises [img] restantes
    custom_image_urls = re.findall(r'\[img\](.+?)\[/img\]', content_without_url)
    # Remplace {STEAM_CLAN_IMAGE} et retourne la première image
    image_urls = [url.replace('{STEAM_CLAN_IMAGE}', 'https://clan.akamai.steamstatic.com/images') for url in custom_image_urls]
    return image_urls[0] if image_urls else None

  @staticmethod
  def _apply_replacements(text: str) -> str:
    """Applique les substitutions de texte pour nettoyer le contenu avec un format simplifié."""
    for pattern, repl in SteamFormatter.REPLACEMENTS.items():
      text = re.sub(pattern, repl, text, flags=re.MULTILINE)
    return text.strip()

  @staticmethod
  def _limit_lines(text: str, max_lines: int = 11) -> str:
    """Limite le texte à un nombre maximum de lignes."""
    lines = text.splitlines()
    return "\n".join(lines[:max_lines])

  @staticmethod
  def _limit_length(text: str, max_length: int) -> str:
      """Tronque le texte à une longueur maximale et supprime les liens dans la dernière ligne si nécessaire."""
      if len(text) > max_length:
        truncated = text[:max_length].rstrip(' \n')
        if re.search(r'https?://\S+', truncated.splitlines()[-1]):
          truncated = ('\n'.join(truncated.splitlines()[:-1])).strip()
        else:
          truncated = truncated + ".."
        return truncated
      return text
  
  @staticmethod
  def _format_links(content: str) -> str:
    """Extrait les liens et remplace les balises de lien par un format simple."""
    content = re.sub(
      r'\[url=(.+?)\](.+?)\[/url\]', 
      lambda m: re.sub(f'[{re.escape(string.punctuation)}]', '', m.group(2)).replace(':', '') + ": " + m.group(1), 
      content
    )
    return content
  
  @staticmethod
  def _filter_lastline(content: str) -> str:
    """Vérifie et supprime la dernière ligne si elle est un titre en gras incomplet."""
    lines = content.splitlines()
    if lines and lines[-1].startswith('**'):
      lines = lines[:-1]
    return '\n'.join(lines).strip()
