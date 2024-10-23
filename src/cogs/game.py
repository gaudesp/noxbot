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
      app_commands.Choice(name=game.game_name[:100], value=str(game.app_id))
      for game in matching_games[:25]
    ]

  @app_commands.autocomplete(game='game_app_id_autocomplete')
  async def game_app_id_autocomplete(self, interaction: discord.Interaction, current: str) -> list[app_commands.Choice]:
    """Complétion automatique pour l'ID des jeux."""
    if not current:
      return []
    matching_games = await self.steam_service.search_game_by_name(current)
    return [
      app_commands.Choice(name=game['name'][:100], value=str(game['appid']))
      for game in matching_games
    ]

  @app_commands.command(name='nx_follow', description='placeholder')
  @app_commands.autocomplete(game=game_app_id_autocomplete)
  @app_commands.checks.has_permissions(administrator=True)
  async def follow_game(self, interaction: discord.Interaction, game: str, channel: discord.TextChannel) -> None:
    """Ajoute un jeu à suivre dans le serveur."""
    app_id = game
    existing_game = await self.game_repository.get_game_for_guild(app_id, interaction.guild.id)
    if existing_game:
      await interaction.response.send_message(self.bot.translate("cogs.game.commands.nx_follow.messages.already_followed", game_name=existing_game.game_name, app_id=existing_game.app_id, channel=existing_game.channel), ephemeral=True)
      return
    game_name = await self.steam_service.get_game_name(app_id)
    if game_name:
      game = await self.game_repository.add_game(app_id=app_id, guild_id=interaction.guild.id, channel_id=channel.id, game_name=game_name)
      await self.news_service.update_last_news(app_id, interaction.guild.id)
      await interaction.response.send_message(self.bot.translate("cogs.game.commands.nx_follow.messages.success", game_name=game.game_name, app_id=game.app_id, channel=game.channel), ephemeral=True)
    else:
      await interaction.response.send_message(self.bot.translate("cogs.game.commands.nx_follow.messages.not_found", game=app_id), ephemeral=True)

  @app_commands.command(name='nx_unfollow', description='placeholder')
  @app_commands.autocomplete(game=game_name_autocomplete)
  @app_commands.checks.has_permissions(administrator=True)
  async def unfollow_game(self, interaction: discord.Interaction, game: str) -> None:
    """Supprime un jeu de la liste des jeux suivis."""
    app_id = game
    game = await self.game_repository.delete_game(app_id=app_id, guild_id=interaction.guild.id)
    if game:
      await interaction.response.send_message(self.bot.translate("cogs.game.commands.nx_unfollow.messages.success", game_name=game.game_name, app_id=game.app_id, channel=game.channel), ephemeral=True)
    else:
      await interaction.response.send_message(self.bot.translate("cogs.game.commands.nx_unfollow.messages.not_followed", game=app_id), ephemeral=True)

  @app_commands.command(name='nx_publish', description='placeholder')
  @app_commands.autocomplete(game=game_name_autocomplete)
  @app_commands.checks.has_permissions(administrator=True)
  async def publish_news(self, interaction: discord.Interaction, game: str) -> None:
    """Publie la dernière actualité d'un jeu dans son channel."""
    app_id = game
    game = await self.game_repository.get_game_for_guild(app_id, interaction.guild.id)
    if game:
      news = await self.news_service.get_last_news(game)
      if news:
        await interaction.response.send_message(self.bot.translate("cogs.game.commands.nx_publish.messages.success", game_name=game.game_name, app_id=game.app_id, channel=game.channel), ephemeral=True)
      else:
        await interaction.response.send_message(self.bot.translate("cogs.game.commands.nx_publish.messages.not_found", game_name=game.game_name), ephemeral=True)
    else:
      await interaction.response.send_message(self.bot.translate("cogs.game.commands.nx_publish.messages.not_exist", game=app_id), ephemeral=True)

  @app_commands.command(name='nx_list', description='placeholder')
  @app_commands.checks.has_permissions(administrator=True)
  async def list_games(self, interaction: discord.Interaction) -> None:
    """Liste tous les jeux suivis dans le serveur."""
    games = await self.game_repository.get_games_for_guild(guild_id=interaction.guild.id)
    if games:
      message = ''.join([self.bot.translate("cogs.game.commands.nx_list.messages.success", game_name=game.game_name, app_id=game.app_id, channel=game.channel) for game in games])
    else:
      message = self.bot.translate("cogs.game.commands.nx_list.messages.not_followed")
    await interaction.response.send_message(message, ephemeral=True)

  @app_commands.command(name='nx_reset', description='placeholder')
  @app_commands.checks.has_permissions(administrator=True)
  async def reset_games(self, interaction: discord.Interaction) -> None:
    """Supprime tous les jeux suivis du serveur."""
    deleted_games = await self.game_repository.delete_all_games(interaction.guild.id)
    if deleted_games:
      await interaction.response.send_message(self.bot.translate("cogs.game.commands.nx_reset.messages.success", total=deleted_games), ephemeral=True)
    else:
      await interaction.response.send_message(self.bot.translate("cogs.game.commands.nx_reset.messages.not_followed"), ephemeral=True)

async def setup(bot: DiscordBot) -> None:
  """Configure le cog de jeu et l'ajoute au bot."""
  await bot.add_cog(GameCog(bot))
