class GameHelper:
  @staticmethod
  def format_followed_games(followed_games):
    return "".join(
      [f"\n- **{game.game.name}** (`{game.game.steam_id}`) ➜ {game.channel}" for game in followed_games]
    )
