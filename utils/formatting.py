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
    r'\[/?(b|u|i|strike)\]': '',  # Supprime toutes les balises [b], [u], [i], [strike] (et leurs fermetures)
    r'\[url=[^\]]+\]\[img.*?\].*?\[/img\]\[/url\]': '', # Supprime les balises [url] qui contiennent une image à l'intérieur
    r'\[url=([^\]]+)\](?!.*\[img.*?\])(.*?)\[/url\]': lambda m: re.sub(f'[{re.escape(string.punctuation)}]', '', m.group(2)).replace(':', '') + ": " + m.group(1), # Supprime les balises [url] qui ne contiennent pas d'image et formate le texte
    r'\[img\].*?\[/img\]\s*(?:(?!.*[\[\]<>\*•◦\/]).{1,100}\n)?': '',
    r'(https?://[^\s\]]*?)[\]\}\)!]+(?=\s|$)': r'\1', # Supprime les caractères invalides en fin d'URL
    r'\[previewyoutube=.*?\]\s*?\[/previewyoutube\]': '', # Supprime les vidéos
    r'\[list\]|\[/*list\]': '', # Supprime les balises de liste 
    r'・([^ ]+)': r'• \1', # Remplace "・" par "•"
    r'(?m)^-\s*': '• ', # Remplace "-" par "•"
    r'\[h([1-6])\](.*?)\[h([1-6])\](.*?)\[/h\3\](.*?)\[/h\1\]': lambda m: "**" + m.group(2).strip() + " · " + m.group(4).strip() + "**", # Formate les titres de type [h1] à [h6] en les joignant avec " · " et en conservant le texte du reste
    r'\[h[1-6]\](.*?)\[/h[1-6]\]': lambda m: "**" + m.group(1).strip() + "**", 
    r'^\d+\.\s+': '\n• ', # Supprime les numéros en début de ligne
    r'[▼=＝]': '', # Supprime les caractères ▼, = et ＝
    r'[\U0001F600-\U0001F64F\U0001F300-\U0001F5FF\U0001F680-\U0001F6FF\U0001F1E0-\U0001F1FF\u2600-\u26FF\u2700-\u27BF\u2B00-\u2BFF\U0001F900-\U0001F9FF\U0001FA70-\U0001FAFF\U0001F700-\U0001F77F]': '', # Supprime tous les emojis et symboles Unicode étendus
    r'^.*⤷.*\n': '', # Supprime les lignes contenant ⤷
    r'\[h[1-6]\]|\[\/h[1-6]\]': '', # Supprime les balises de titre [h1] à [h6]
    r'^\s*\[\s*(.*?)\s*\]*(?=\n• )': r'\1', # Convertit les balises [] en titres si suivi d'une liste
    r'\[.*?\]': '', # Supprime les autres balises [xxx] restantes
    r'/((?:h[1-6]|b|u|i|strike))(?=\s|$)': '',  # Supprime les noms de balises résiduels (/h1…/h6, /b, /u, /i, /strike)
    r'^\s*#+\s*\n*(.*?)\n*#+\s*$': r'\n\1', # Supprime les symboles de titre (comme ####) et garde uniquement le texte entre les symboles
    r'(?<=\S)\n{2,}(?=\s*•)': '\n', # Supprime les sauts de ligne multiples avant un élément de liste
    r'(?m)^\s*(?!(?:[\•]|\*\*))(.+?)(:?)\s*(?=\n\s*•)': lambda m: f"\n**{m.group(1).strip().title()}**{m.group(2)}", # Formate les titres en gras
    r'_+': lambda m: '' if len(m.group()) > 1 else m.group(),  # Supprime seulement les underscores consécutifs
    r'([.])\1+': lambda m: m.group(1) if len(m.group()) > 1 else m.group(),  # Supprime les points consécutifs
    r'^[\s]+\n': '\n', # Supprime les lignes vides en début de texte
    r'[\n]{2,}': '\n\n', # Réduit les sauts de ligne multiples à un seul
    r'[\[\]]': '', # Supprime tous les crochets restants
    ' {2,}': ' ', # Réduit les espaces multiples à un seul
    r'’': "'",  # Normalize les apostrophes
  }

  @staticmethod
  def clean_content(content: str, max_length: int = 500) -> str:
    log.debug(f"Input : \"{content}\"")
    format_list_block = SteamFormatter._format_list_block(content)
    print(f"format_list_block : \"{format_list_block}\"")
    apply_replacements = SteamFormatter._apply_replacements(format_list_block)
    print(f"apply_replacements : \"{apply_replacements}\"")
    no_duplicate_urls = SteamFormatter._remove_duplicate_urls(apply_replacements)
    print(f"no_duplicate_urls : \"{no_duplicate_urls}\"")
    limited = SteamFormatter._limit(no_duplicate_urls, max_chars=max_length, max_lines=12)
    print(f"limited : \"{limited}\"")
    cleaned_content = SteamFormatter._final_filter(limited)
    print(f"cleaned_content : \"{cleaned_content}\"")
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
  def _final_filter(content: str) -> str:
    lines = content.splitlines()
    filtered = []
    i = 0
    while i < len(lines):
      raw = lines[i]
      indent = raw[: len(raw) - len(raw.lstrip('\u00A0 '))]
      stripped = raw.strip()
      if stripped.startswith('**') and stripped.endswith('**') and stripped.count('**') == 2:
        filtered.append(stripped)
        i += 1
        continue
      if stripped.startswith('**') and stripped.endswith('**'):
        next_stripped = lines[i + 1].strip() if i + 1 < len(lines) else '' 
        if not next_stripped.startswith('•'): 
          i += 1 
          continue
      if 'http' in stripped and stripped.endswith('..'):
        parts = stripped.split()
        if parts and parts[-1].startswith('http') and parts[-1].endswith('..'):
          prefix = ' '.join(parts[:-1]).rstrip(' :;,')
          stripped = prefix + '..'
      filtered.append(indent + stripped)
      i += 1
    final_lines = []
    for ln in filtered:
      if ln == '...':
        while final_lines and final_lines[-1] == '':
          final_lines.pop()
        final_lines.append(ln)
      else:
        final_lines.append(ln)
    while final_lines and final_lines[-1] == '':
      final_lines.pop()
    return '\n'.join(final_lines)

  @staticmethod
  def _format_list_block(text: str) -> str:
    text = re.sub(r'(?<!\n)\[list\]', '\n[list]', text)
    text = re.sub(r'(?<!\n)\[/list\]', '\n[/list]', text)
    text = re.sub(r'(?<!\n)\[\*\]\s*', '\n[*] ', text)
    lines = text.splitlines()
    formatted = []
    depth = 0
    for raw in lines:
      stripped = raw.strip()
      if not stripped:
        formatted.append(raw)
        continue
      if stripped == "[list]":
        depth += 1
      elif stripped == "[/list]":
        depth = max(depth - 1, 0)
      elif stripped.startswith("[*]"):
        content = stripped[3:].strip()
        bullet = '\u00A0' * ((depth - 1) * 4) + ('•' if depth <= 1 else '◦')
        formatted.append(f"{bullet} {content}")
      else:
        formatted.append(raw)
        depth = 0
    return "\n".join(formatted).strip()
    
  @staticmethod
  def _remove_duplicate_urls(text: str) -> str:
    urls_seen = set()
    output = []
    for line in text.splitlines():
      urls_in_line = re.findall(r'https?://[^\s\]\)\}]+', line)
      keep_line = line
      for url in urls_in_line:
        if url in urls_seen:
          keep_line = keep_line.replace(url, '')
        else:
          urls_seen.add(url)
      output.append(keep_line.rstrip())
    cleaned_text = '\n'.join(output)
    cleaned_text = re.sub(r'\n{3,}', '\n\n', cleaned_text)
    return cleaned_text.strip()
