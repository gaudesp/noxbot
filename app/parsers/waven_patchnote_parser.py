from datetime import datetime
from bs4 import BeautifulSoup
from lib.logging import Logger
from models.waven.patchnote import WavenPatchnote

patchnote_model = WavenPatchnote()
logger = Logger('parser')

class WavenPatchnoteParser:
  def __init__(self, data):
      self.title = None
      self.url = None
      self.date = None
      self.reply = None
      self.patchnotes = []
      self.parser = BeautifulSoup(data, 'html.parser')

  def find_patchnotes(self):
    trs = self.parser.find_all('tr')
    if patchnote_model.count() == len(trs):
      return self.patchnotes
    
    self.find_rows(trs)
    self.save_patchnote()

    return self.patchnotes

  def save_patchnote(self):
    if self.patchnotes:
      patchnote_model.save({'list': self.patchnotes + patchnote_model.find_all()})
  
  def find_rows(self, rows):
    for row in rows:
      element = self.find_columns(row)
      if element and 'version' in element['title'].lower() \
        and 'alpha' not in element['title'].lower() \
        and int(self.reply) > 0 \
        and element not in patchnote_model.find_all():
          logger.log(element)
          self.patchnotes.append(element)

  def find_columns(self, row):
    id = 0
    for column in row.find_all('td'):
      self.find_reply(column, id)
      self.find_date(column)
      self.find_info(column)
      id = id + 1
    return self.format_result()
    
  def find_reply(self, column, id):
    if id == 1:
      self.reply = column.text
  
  def find_date(self, column):
    for date in column.find_all('a', { 'class': 'ak-tooltip' }):
      self.date = date.text

  def find_info(self, column):
    for info in column.find_all('div', { 'class': 'ak-content-text-topic' }):
      self.find_title(info)
      self.find_url(info)
  
  def find_title(self, info):
    self.title = info.text.strip("\n").split("\n")[0]
  
  def find_url(self, info):
    for url in info.find_all('a', { 'class': 'ak-title-topic' }):
      self.url = url['href']

  def format_result(self):
    if None not in (self.title, self.url, self.date):
      self.url = f"https://forum.waven-game.com{self.url}"
      self.date = self.format_date().strftime("%d/%m/%Y")
      
      return {'title': self.title, 'url': self.url, 'date': self.date}

  def format_date(self):
    if 'Today' in self.date:
      return datetime.now()
    
    return datetime.strptime(self.date, '%B %d, %Y, %H:%M:%S')
