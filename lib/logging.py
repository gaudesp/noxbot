import os
import logging

class Logger:
  def __init__(self, subname):
    self.name = 'discord'
    self.output = './log/discord.log'
    self.subname = subname
    self.logger = self.logging()

  def handler(self):
    os.makedirs(os.path.dirname(self.output), exist_ok = True)
    handler = logging.FileHandler(filename = self.output, encoding = 'utf-8')
    handler.setFormatter(logging.Formatter('%(asctime)s:%(levelname)s:%(name)s: %(message)s'))
    return handler
  
  def logging(self):
    logger = logging.getLogger(f"discord.{self.subname}")
    logger.addHandler(self.handler())
    return logger

  def log(self, message):
    self.logger.info(message)
