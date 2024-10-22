# src/cogs/game.py
import discord
from discord.ext import commands, tasks
from discord import app_commands
from src.repositories.game import GameRepository
from src.services.steam import SteamService
from src.services.news import NewsService
from src.utils.discord import DiscordBot

class GameCog(commands.Cog):
  def __init__(self, bot: DiscordBot) -> None:
    """Initialise le cog de jeu avec une instance de DiscordBot."""
    self.bot = bot
    self.game_repository = GameRepository(bot)
    self.steam_service = SteamService()
    self.news_service = NewsService(bot)
    self.check_for_news.start()

  @commands.Cog.listener()
  async def on_ready(self) -> None:
    """Événement déclenché lorsque le bot est prêt."""
    await self.__followed_games()

  async def __followed_games(self) -> None:
    """Vérifie et enregistre les jeux suivis dans les logs."""
    games = {(game.app_id, game.game_name) for game in await self.game_repository.get_all_games()}
    games_info = ', '.join(f'{name} (ID: {app_id})' for app_id, name in games)
    games_total = len(games)
    self.bot.log(f"{games_total} followed games {':' if games_total > 0 else ''} {games_info}", "discord.followed_games")

  @tasks.loop(seconds=3600)
  async def check_for_news(self) -> None:
    """Vérifie les actualités des jeux toutes les heures."""
    await self.news_service.get_all_news()
    self.bot.log("Steam games news verified", "discord.check_for_news")

  @check_for_news.before_loop
  async def before_check_for_news(self) -> None:
    """Attendre que le bot soit prêt avant de démarrer la boucle de vérification des actualités."""
    await self.bot.wait_until_ready()
    self.check_for_news.change_interval(seconds=self.bot.settings.check_interval)
  
  @app_commands.autocomplete(game='game_name_autocomplete')
  async def game_name_autocomplete(self, interaction: discord.Interaction, current: str) -> list[app_commands.Choice]:
    """Complétion automatique pour le nom des jeux."""
    games = await self.game_repository.get_games_for_guild(interaction.guild.id)
    matching_games = [game for game in games if current.lower() in game.game_name.lower()]
    return [
      app_commands.Choice(name=game.game_name, value=str(game.app_id))
      for game in matching_games[:25]
    ]

  @app_commands.autocomplete(game='game_app_id_autocomplete')
  async def game_app_id_autocomplete(self, interaction: discord.Interaction, current: str) -> list[app_commands.Choice]:
    """Complétion automatique pour l'ID des jeux."""
    if not current:
      return []
    matching_games = await self.steam_service.search_game_by_name(current)
    return [
      app_commands.Choice(name=game['name'], value=str(game['appid']))
      for game in matching_games
    ]

  @app_commands.command(name='follow_game', description='Ajoutez un jeu à suivre')
  @app_commands.autocomplete(game=game_app_id_autocomplete)
  @app_commands.checks.has_permissions(administrator=True)
  async def follow_game(self, interaction: discord.Interaction, game: str, channel: discord.TextChannel) -> None:
    """Ajoute un jeu à suivre dans le serveur."""
    app_id = game
    existing_game = await self.game_repository.get_game_for_guild(app_id, interaction.guild.id)
    if existing_game:
      await interaction.response.send_message(
        f"Le jeu **{existing_game.game_name}** (`{existing_game.app_id}`) est déjà suivi dans {existing_game.channel}.",
        ephemeral=True
      )
      return
    game_name = await self.steam_service.get_game_name(app_id)
    if game_name:
      game = await self.game_repository.add_game(app_id=app_id, guild_id=interaction.guild.id, channel_id=channel.id, game_name=game_name)
      await self.news_service.update_last_news(app_id, interaction.guild.id)
      await interaction.response.send_message(f"Le jeu **{game.game_name}** (`{game.app_id}`) sera désormais suivi dans {game.channel}.", ephemeral=True)
    else:
      await interaction.response.send_message(f"Le jeu `{app_id}` n'existe pas.",ephemeral=True)

  @app_commands.command(name='unfollow_game', description='Supprimez un jeu suivi')
  @app_commands.autocomplete(game=game_name_autocomplete)
  @app_commands.checks.has_permissions(administrator=True)
  async def unfollow_game(self, interaction: discord.Interaction, game: str) -> None:
    """Supprime un jeu de la liste des jeux suivis."""
    app_id = game
    game = await self.game_repository.delete_game(app_id=app_id, guild_id=interaction.guild.id)
    if game:
      await interaction.response.send_message(f"Le jeu **{game.game_name}** (`{game.app_id}`) ne sera plus suivi dans {game.channel}.", ephemeral=True)
    else:
      await interaction.response.send_message(f"Le jeu `{app_id}` n'est pas suivi.", ephemeral=True)

  @app_commands.command(name='publish_news', description="Postez la dernière actualité du jeu dans son channel (pour tester)")
  @app_commands.autocomplete(game=game_name_autocomplete)
  @app_commands.checks.has_permissions(administrator=True)
  async def publish_news(self, interaction: discord.Interaction, game: str) -> None:
    """Publie la dernière actualité d'un jeu dans son channel."""
    app_id = game
    game = await self.game_repository.get_game_for_guild(app_id, interaction.guild.id)
    if game:
      news = await self.news_service.get_last_news(game)
      if news:
        await interaction.response.send_message(f"La dernière actualité du jeu **{game.game_name}** a été publiée dans le channel {game.channel}.", ephemeral=True)
      else:
        await interaction.response.send_message(f"Aucune nouvelle actualité n'a été trouvée pour le jeu **{game.game_name}**.", ephemeral=True)
    else:
      await interaction.response.send_message(f"Le jeu `{app_id}` n'existe pas.", ephemeral=True)

  @app_commands.command(name='list_game', description='Listez les jeux suivis')
  @app_commands.checks.has_permissions(administrator=True)
  async def list_games(self, interaction: discord.Interaction) -> None:
    """Liste tous les jeux suivis dans le serveur."""
    games = await self.game_repository.get_games_for_guild(guild_id=interaction.guild.id)
    if games:
      game_list = '\n'.join([f"**{game.game_name}** (`{game.app_id}`) dans {game.channel}" for game in games])
      await interaction.response.send_message(f"Jeux suivis sur ce serveur:\n{game_list}", ephemeral=True)
    else:
      await interaction.response.send_message("Aucun jeu n'est suivi.", ephemeral=True)

  @app_commands.command(name='reset_games', description='Supprimez tous les jeux suivis du serveur')
  @app_commands.checks.has_permissions(administrator=True)
  async def reset_games(self, interaction: discord.Interaction) -> None:
    """Supprime tous les jeux suivis du serveur."""
    deleted_games = await self.game_repository.delete_all_games(interaction.guild.id)
    if deleted_games:
      await interaction.response.send_message(f"{deleted_games} jeux ne seront plus suivis.", ephemeral=True)
    else:
      await interaction.response.send_message("Aucun jeu à supprimer.", ephemeral=True)

async def setup(bot: DiscordBot) -> None:
  """Configure le cog de jeu et l'ajoute au bot."""
  await bot.add_cog(GameCog(bot))
