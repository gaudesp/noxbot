# src/cogs/game.py
import discord
from discord.ext import commands, tasks
from discord import app_commands
from src.services.game import GameService
from src.services.steam import SteamService
from src.services.news import NewsService
from src.utils.discord import DiscordBot

class GameCog(commands.Cog):
  def __init__(self, bot: DiscordBot) -> None:
    """Initialise le cog de jeu avec les services nécessaires."""
    self.bot = bot
    self.steam_service = SteamService()
    self.game_service = GameService(bot)
    self.news_service = NewsService(bot, self.game_service)
    self.check_for_news.start()

  @commands.Cog.listener()
  async def on_ready(self) -> None:
    """Événement appelé lorsque le bot est prêt."""
    await self.__followed_games()

  async def __followed_games(self) -> None:
    """Récupère et journalise les jeux suivis par le bot."""
    games = {(game.id, game.name) for game in await self.game_service.find_all_games()}
    games_info = ', '.join(f'{name} (ID: {id})' for id, name in games)
    games_total = len(games)
    self.bot.log(f"{games_total} followed games {':' if games_total > 0 else ''} {games_info}", "discord.followed_games")

  @tasks.loop(seconds=3600)
  async def check_for_news(self) -> None:
    """Vérifie les actualités des jeux toutes les heures."""
    await self.news_service.get_all_news()
    self.bot.log("Steam games news verified", "discord.check_for_news")

  @check_for_news.before_loop
  async def before_check_for_news(self) -> None:
    """Attend que le bot soit prêt avant de démarrer la vérification des actualités."""
    await self.bot.wait_until_ready()
    self.check_for_news.change_interval(seconds=self.bot.settings.check_interval)

  @app_commands.autocomplete(game='game_name_autocomplete')
  async def game_name_autocomplete(self, interaction: discord.Interaction, current: str) -> list[app_commands.Choice]:
    """Propose des complétions pour les noms de jeux en fonction de l'entrée de l'utilisateur."""
    await interaction.response.defer(thinking=True)
    games = await self.game_service.find_games_for_guild(interaction.guild.id)
    matching_games = [game for game in games if current.lower() in game.name.lower()]
    choices = [
      app_commands.Choice(name=game.name[:100], value=str(game.id))
      for game in matching_games[:25]
    ]
    await interaction.response.autocomplete(choices)

  @app_commands.autocomplete(game='game_app_id_autocomplete')
  async def game_app_id_autocomplete(self, interaction: discord.Interaction, current: str) -> list[app_commands.Choice]:
    """Propose des complétions pour les IDs d'applications de jeux."""
    matching_games = await self.steam_service.search_game_by_name(current)
    choices = [
      app_commands.Choice(name=game['name'][:100], value=str(game['appid']))
      for game in matching_games
    ]
    await interaction.response.autocomplete(choices)

  @app_commands.command(name='nx_follow', description='placeholder')
  @app_commands.autocomplete(game=game_app_id_autocomplete)
  @app_commands.checks.has_permissions(administrator=True)
  async def follow(self, interaction: discord.Interaction, game: str, channel: discord.TextChannel) -> None:
    """Permet de suivre un jeu spécifique."""
    game_exist = await self.game_service.find_game_for_guild(game, interaction.guild.id)
    if game_exist:
      await interaction.response.send_message(self.bot.i18n.translate("cogs.game.commands.nx_follow.messages.exist", game_name=game_exist.name, channel=game_exist.channel), ephemeral=True)
      return

    game_found = await self.steam_service.get_game_name(game)
    if not game_found:
      await interaction.response.send_message(self.bot.i18n.translate("cogs.game.commands.nx_follow.messages.not_found"), ephemeral=True)
      return
    
    new_game = await self.game_service.add_game(game, interaction.guild.id, channel.id, game_found)
    await interaction.response.send_message(self.bot.i18n.translate("cogs.game.commands.nx_follow.messages.success", game_name=new_game.name, channel=new_game.channel), ephemeral=True)

  @app_commands.command(name='nx_unfollow', description='placeholder')
  @app_commands.autocomplete(game=game_name_autocomplete)
  @app_commands.checks.has_permissions(administrator=True)
  async def unfollow_game(self, interaction: discord.Interaction, game: str) -> None:
    """Permet d'arrêter de suivre un jeu spécifique."""
    game_followed = await self.game_service.delete_game(app_id=game, guild_id=interaction.guild.id)
    if not game_followed:
      await interaction.response.send_message(self.bot.i18n.translate("cogs.game.commands.nx_unfollow.messages.not_followed"), ephemeral=True)
      return
    
    await interaction.response.send_message(self.bot.i18n.translate("cogs.game.commands.nx_unfollow.messages.success", game_name=game_followed.name, channel=game_followed.channel), ephemeral=True)

  @app_commands.command(name='nx_publish', description='placeholder')
  @app_commands.autocomplete(game=game_name_autocomplete)
  @app_commands.checks.has_permissions(administrator=True)
  async def publish_news(self, interaction: discord.Interaction, game: str) -> None:
    """Publie les dernières nouvelles d'un jeu suivi."""
    game_exist = await self.game_service.find_game_for_guild(game, interaction.guild.id)
    if not game_exist:
      await interaction.response.send_message(self.bot.i18n.translate("cogs.game.commands.nx_publish.messages.not_exist", game_name=game), ephemeral=True)
      return

    news_found = await self.news_service.get_last_news(game_exist)
    if not news_found:
      await interaction.response.send_message(self.bot.i18n.translate("cogs.game.commands.nx_publish.messages.not_found", game_name=game_exist.name), ephemeral=True)
      return

    await interaction.response.send_message(self.bot.i18n.translate("cogs.game.commands.nx_publish.messages.success", game_name=game_exist.name, channel=game_exist.channel), ephemeral=True)

  @app_commands.command(name='nx_list', description='placeholder')
  @app_commands.checks.has_permissions(administrator=True)
  async def list_games(self, interaction: discord.Interaction) -> None:
    """Liste tous les jeux suivis pour le serveur."""
    games_followed = await self.game_service.find_games_for_guild(guild_id=interaction.guild.id)
    if not games_followed:
      await interaction.response.send_message(self.bot.i18n.translate("cogs.game.commands.nx_list.messages.not_followed"), ephemeral=True)
      return
    
    await interaction.response.send_message(''.join([self.bot.i18n.translate("cogs.game.commands.nx_list.messages.success", game_name=game.name, app_id=game.id, channel=game.channel) for game in games_followed]), ephemeral=True)

  @app_commands.command(name='nx_reset', description='placeholder')
  @app_commands.checks.has_permissions(administrator=True)
  async def reset_games(self, interaction: discord.Interaction) -> None:
    """Réinitialise la liste des jeux suivis pour le serveur."""
    games_followed = await self.game_service.delete_games(interaction.guild.id)
    if not games_followed:
      await interaction.response.send_message(self.bot.i18n.translate("cogs.game.commands.nx_reset.messages.not_followed"), ephemeral=True)
      return
    
    await interaction.response.send_message(self.bot.i18n.translate("cogs.game.commands.nx_reset.messages.success", games=games_followed), ephemeral=True)

async def setup(bot: DiscordBot) -> None:
  """Configure le cog de jeux avec le bot."""
  await bot.add_cog(GameCog(bot))
