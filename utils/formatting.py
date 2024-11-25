from datetime import datetime
import re
import string

class SteamFormatter:
  """Classe utilitaire pour le formatage de texte, nettoyage de contenu et gestion des émojis."""

  REPLACEMENTS = {
    r'\[b\](.*?)(?=\[/?b\]|$)': r'\1',  # Supprime les balises [b]
    r'\[u\](.*?)(?=\[/?u\]|$)': r'\1',  # Supprime les balises [u]
    r'\[i\](.*?)(?=\[/?i\]|$)': r'\1',  # Supprime les balises [i]
    r'\[strike\](.*?)(?=\[/?strike\]|$)': r'\1',  # Supprime les balises [strike]
    r'\[img\].*?\[/img\]': '',  # Supprime les images
    r'\[url=.*?\].*?\[/url\]': '',  # Supprime les liens [url]
    r'\[previewyoutube=.*?\]\s*?\[/previewyoutube\]': '',  # Supprime les vidéos
    r'\[list\]|\[/*list\]': '',  # Supprime les balises de liste
    r'\s*\[\*\](?=\S)': '\n- ',  # Convertit les éléments principaux en puces
    r'\s*\[\*\]\s*': '\n- ',  # Corrige les sous-listes en puces
    r'((?:\[h[1-6]\].*?\[/h[1-6]\]\s*)+)(.*)': lambda m: ' · '.join(re.sub(r'\[h[1-6]\](.*?)\[/h[1-6]\]', r'\1', m.group(1)).strip().split('\n')) + '\n' + m.group(2),
    r'^\d+\.\s+': '',  # Supprime les numéros en début de ligne
    r'[▼==]': '',  # Supprime les caractères ▼ et ==
    r'・([^ ]+)': r'- \1',  # Remplace "・" par "-"
    r'^.*⤷.*\n': '',  # Supprime les lignes contenant ⤷
    r'\[h[1-6]\]|\[\/h[1-6]\]': '',  # Supprime les balises de titre [h1] à [h6]
    r'^\s*\[\s*(.*?)\s*\]\s*(?=\n- )': r'\1',  # Convertit les balises [] en titres si suivi d'une liste
    r'\[.*?\]': '',  # Supprime les autres balises
    r'^\s*#+\s*\n*(.*?)\n*#+\s*$': r'\n\1',
    r'(?<=\S)\n{2,}(?=\s*-)': '\n',
    r'^(?!- )(.*?)(?=\n- )': lambda match: f"**{match.group(1).title()}**" if match.group(1).strip() else match.group(1), # Formate les titres en gras
    r'imgSTEAMCLANIMAGE.*?jpgimg:': '',  # Supprime les images Steam spécifiques
    r'[\n\s]{2,}': '\n\n',  # Réduit les espaces multiples à un seul saut de ligne
  }

  @staticmethod
  def clean_content(content: str, max_length: int = 500) -> str:
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
    """Convertit un timestamp en objet datetime."""
    return datetime.fromtimestamp(timestamp)

  @staticmethod
  def extract_image(content: str) -> str:
      """Récupère la première image valide non GIF."""
      content_without_url = re.sub(r'\[url=.*?\].*?\[/url\]', '', content, flags=re.DOTALL)
      custom_image_urls = re.findall(r'\[img\](.+?)\[/img\]', content_without_url)
      image_urls = [
        url.replace('{STEAM_CLAN_IMAGE}', 'https://clan.akamai.steamstatic.com/images')
        for url in custom_image_urls if not url.lower().endswith('.gif')
      ]
      return image_urls[0] if image_urls else None

  @staticmethod
  def _apply_replacements(text: str) -> str:
    """Applique les remplacements définis dans REPLACEMENTS."""
    for pattern, repl in SteamFormatter.REPLACEMENTS.items():
      text = re.sub(pattern, repl, text, flags=re.MULTILINE)
    return text.strip()

  @staticmethod
  def _limit_lines(text: str, max_lines: int = 15) -> str:
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
  def _format_links(content: str) -> str:
    """Formate les liens en un texte simple."""
    content = re.sub(
      r'\[url=(.+?)\](.+?)\[/url\]', 
      lambda m: re.sub(f'[{re.escape(string.punctuation)}]', '', m.group(2)).replace(':', '') + ": " + m.group(1), 
      content
    )
    return content
  
  @staticmethod
  def _filter_lastline(content: str) -> str:
    """Supprime une dernière ligne incomplète ou mal formattée."""
    lines = content.splitlines()
    if lines and lines[-1].startswith('**'):
      lines = lines[:-1]
    return '\n'.join(lines).strip()
