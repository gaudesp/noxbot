from datetime import datetime
from PIL import Image
from io import BytesIO
import re
import string

import requests
from utils.logging import logger

log = logger.get_logger(__name__)

class SteamFormatter:
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
    r'・([^ ]+)': r'• \1', # Remplace "・" par "•"
    r'((?:\[h[1-6]\].*?\[/h[1-6]\]\s*)+)(.*)': lambda m: ' · '.join(re.findall(r'\[h[1-6]\](.*?)\[/h[1-6]\]', m.group(1))) + '\n' + m.group(2), # Formate les titres de type [h1] à [h6] en les joignant avec " · " et en conservant le texte du reste
    r'^\d+\.\s+': '\n• ', # Supprime les numéros en début de ligne
    r'[▼=＝]': '', # Supprime les caractères ▼, = et ＝
    r'[\U00010000-\U0010FFFF]': '', # Supprime tous les emojis et symboles Unicode étendus
    r'^.*⤷.*\n': '', # Supprime les lignes contenant ⤷
    r'\[h[1-6]\]|\[\/h[1-6]\]': '', # Supprime les balises de titre [h1] à [h6]
    r'^\s*\[\s*(.*?)\s*\]*(?=\n• )': r'\1', # Convertit les balises [] en titres si suivi d'une liste
    r'\[.*?\]': '', # Supprime les autres balises [xxx] restantes
    r'^\s*#+\s*\n*(.*?)\n*#+\s*$': r'\n\1', # Supprime les symboles de titre (comme ####) et garde uniquement le texte entre les symboles
    r'(?<=\S)\n{2,}(?=\s*•)': '\n', # Supprime les sauts de ligne multiples avant un élément de liste
    r'(?m)^(?![\•\s])(.+?)(?=\s*\n\s*•)': lambda match: f"\n**{match.group(1).title()}**" if match.group(1).strip() else match.group(1), # Formate les titres en gras
    r'^[\s]+\n': '\n', # Supprime les lignes vides en début de texte
    r'[\n]{2,}': '\n\n', # Réduit les sauts de ligne multiples à un seul
    r'[\[\]]': '', # Supprime tous les crochets restants
    ' {2,}': ' ', # Réduit les espaces multiples à un seul
  }

  @staticmethod
  def clean_content(content: str, max_length: int = 500) -> str:
    log.debug(f"Input : \"{content}\"")
    format_list_block = SteamFormatter._format_list_block(content)
    apply_replacements = SteamFormatter._apply_replacements(format_list_block)
    limited = SteamFormatter._limit(apply_replacements,
                                    max_chars=max_length,
                                    max_lines=12)
    cleaned_content = SteamFormatter._filter_lastline(limited)
    log.debug(f"Output : \"{cleaned_content}\"")
    return cleaned_content
  
  @staticmethod
  def clean_date(timestamp: datetime):
    return datetime.fromtimestamp(timestamp)
  
  @staticmethod
  def extract_image(content: str, min_width: int = 460, min_height: int = 215) -> str:
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
    for pattern, repl in SteamFormatter.REPLACEMENTS.items():
      text = re.sub(pattern, repl, text, flags=re.MULTILINE)
    return text.strip()

  @staticmethod
  def _limit(text: str, max_chars: int, max_lines: int) -> str:
      lines = text.splitlines()
      out, total = [], 0
      for idx, line in enumerate(lines):
          if idx >= max_lines or total >= max_chars:
              break
          remaining = max_chars - total
          if len(line) + 1 <= remaining:
              out.append(line)
              total += len(line) + 1
          else:
              out.append(line[:remaining].rstrip() + '..')
              total = max_chars
              break
      result = "\n".join(out).rstrip()
      if len(out) < len(lines) or total < len(text):
          result += "\n..."
      return result
  
  @staticmethod
  def _filter_lastline(content: str) -> str:
    lines = content.splitlines()
    if lines and lines[-1].startswith('**'):
      lines = lines[:-1]
    return '\n'.join(lines).strip()
          
  @staticmethod
  def _format_list_block(text: str) -> str:
    lines = text.splitlines()
    formatted, depth = [], 0
    for line in lines:
      stripped = line.strip()
      if stripped == "[list]":
        depth += 1
      elif stripped == "[/list]":
        depth = max(depth - 1, 0)
      elif stripped.startswith("[*]"):
        match = re.match(r'\[\*\]\s*(.*)', stripped)
        content = match.group(1).strip() if match else ''
        bullet = f"{'\u00A0' * (depth - 1) * 4}{'•' if depth <= 1 else '◦'}"
        formatted.append(f"{bullet} {content}")
      else:
        formatted.append(stripped)
        depth = 0
    return "\n".join(formatted).strip()
