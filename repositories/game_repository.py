# repositories/game_repository.py
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from config import DB_PATH
from models.game_model import GameModel

engine = create_engine(f'sqlite:///{DB_PATH}')
Session = sessionmaker(bind=engine)

def init_db():
  GameModel.__table__.create(bind=engine, checkfirst=True)

def add_game(app_id, guild_id, channel_id, game_name):
  with Session() as session:
    game = GameModel(app_id=app_id, guild_id=guild_id, channel_id=channel_id, game_name=game_name)
    session.add(game)
    session.commit()
    session.refresh(game)
    return game

def get_all_games():
  with Session() as session:
    games = session.query(GameModel).all()
    return games

def get_games_for_guild(guild_id):
  with Session() as session:
    games = session.query(GameModel).filter_by(guild_id=guild_id).all()
    return games

def get_game_for_guild(app_id, guild_id):
  with Session() as session:
    game = session.query(GameModel).filter_by(app_id=app_id, guild_id=guild_id).first()
    return game

def update_last_news_id(app_id, guild_id, news_id):
  with Session() as session:
    game = session.query(GameModel).filter_by(app_id=app_id, guild_id=guild_id).first()
    if game:
      game.last_news_id = news_id
      session.commit()

def delete_game(app_id, guild_id):
  with Session() as session:
    game = session.query(GameModel).filter_by(app_id=app_id, guild_id=guild_id).first()
    if game:
      session.delete(game)
      session.commit()
      session.close()
      return game
    return None
  
def delete_all_games(guild_id):
  with Session() as session:
    games = session.query(GameModel).filter_by(guild_id=guild_id).all()
    if games:
      for game in games:
        session.delete(game)
      session.commit()
      return len(games)
  return None
