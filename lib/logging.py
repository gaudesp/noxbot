import os
import logging

class Logger:
  def __init__(self, subname):
    self.name = 'discord'
    #il faudrait mettre l'output en param dans un fichier à part (ou en variable d'environnement éventuellement) et de manière générale regrouper tous les params dans un endroit unique
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
#ça pourrait être intéressant de te faire une fonction logInfo et une fonction logErr, voir même une fonction qui prendre le logLevel en param si tu veux logger autre chose que de l'info
  def log(self, message):
    self.logger.info(message)
