from lib.file import File

class DiscordServer:
  def __init__(self):
    self.storage = './db/discord/server.json'
    self.data = File(self.storage).read()

  #tu peux utiliser la syntaxe "ternaire" :
  # return value_if_true if condition else value_if_false
  # ce qui donne : 
  # return [] if self.data['list'] is None else self.data['list']
  def find_all(self):
    if self.data['list'] is None:
      return []
    return self.data['list']

  
  def count(self):
    if self.data['list'] is None:
      return 0
    return len(self.data['list'])

  def save(self, value):
    File(self.storage).store(value)
