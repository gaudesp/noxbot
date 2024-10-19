# src/helpers/news_helper.py
from bs4 import BeautifulSoup
import re

def clean_news_content(contents):
  soup = BeautifulSoup(contents, 'html.parser')
  cleaned_contents = soup.get_text(separator=' ', strip=True)

  cleaned_contents = re.sub(r'\[img\].*?\[/img\]', '', cleaned_contents)
  cleaned_contents = re.sub(r'\[previewyoutube=.*?\]\s*?\[/previewyoutube\]', '', cleaned_contents)
  cleaned_contents = re.sub(r'\[.*?\]', '', cleaned_contents)
  cleaned_contents = re.sub(r'\s+', ' ', cleaned_contents).strip()
  cleaned_contents = re.sub(r'^\d+\.\s*', '', cleaned_contents, flags=re.MULTILINE)

  return cleaned_contents

def extract_image_urls(contents):
  soup = BeautifulSoup(contents, 'html.parser')
  image_urls = [img['src'] for img in soup.find_all('img')]

  custom_image_urls = re.findall(r'\[img\](.+?)\[/img\]', contents)
  image_urls += [url.replace('{STEAM_CLAN_IMAGE}', 'https://clan.akamai.steamstatic.com/images') for url in custom_image_urls]

  return image_urls
