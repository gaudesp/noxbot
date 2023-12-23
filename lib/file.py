import json
import magic
from lib.logging import Logger

logger = Logger('file')

class File:
  def __init__(self, path):
    self.path = path
    self.content_type = magic.Magic(mime = True).from_file(self.path)

  def read(self):
    logger.log(f"Reading {self.path}")
    file = open(self.path, 'r')
    return self.load(file)
  
  def store(self, data):
    logger.log(f"Storing data to {self.path}")
    with open(self.path, 'w') as outfile: 
      self.write(data, outfile)
    #le mot clé "with" fait en sorte de fermer automatiquement le fichier ? dans le cas contraire, petite fuite mémoire

  def load(self, file):
    if 'application/json' in self.content_type:
      return json.load(file)
    elif 'text/html' in self.content_type:
      return file.read()
  
  def write(self, data, file):
    if 'application/json' in self.content_type:
      return json.dump(data, file, indent = 2)
    elif 'text/html' in self.content_type:
      return file.write(data)
