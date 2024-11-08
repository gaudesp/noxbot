# src/cogs/game.py
import discord
from discord.ext import commands, tasks
from discord import app_commands
from src.services.guild import GuildService
from src.services.game import GameService
from src.services.steam import SteamService
from src.services.news import NewsService
from src.utils.discord import DiscordBot
from src.utils.i18n import I18n

class GameCog(commands.Cog):
  def __init__(self, bot: DiscordBot) -> None:
    """Initialise le cog de jeu avec les services nécessaires."""
    self.bot = bot
    self.steam_service = SteamService()
    self.game_service = GameService(bot)
    self.guild_service = GuildService(bot)
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
    self.bot.log(message=f"{games_total} followed games {':' if games_total > 0 else ''} {games_info}", name="discord.followed_games")

  @tasks.loop(seconds=3600)
  async def check_for_news(self) -> None:
    """Vérifie les actualités des jeux toutes les heures."""
    await self.news_service.send_all_news()
    self.bot.log(message="Steam games news verified", name="discord.check_for_news")

  @check_for_news.before_loop
  async def before_check_for_news(self) -> None:
    """Attend que le bot soit prêt avant de démarrer la vérification des actualités."""
    await self.bot.wait_until_ready()
    self.check_for_news.change_interval(seconds=self.bot.settings.check_interval)

  async def game_name_autocomplete(self, interaction: discord.Interaction, current: str) -> list[app_commands.Choice]:
    """Propose des complétions pour les noms de jeux en fonction de l'entrée de l'utilisateur."""
    games = await self.game_service.find_games_for_guild(interaction.guild.id)
    return [
      app_commands.Choice(name=game.name[:100], value=str(game.id))
      for game in games if current.lower() in game.name.lower()
    ][:25] if games else []

  async def game_app_id_autocomplete(self, interaction: discord.Interaction, current: str) -> list[app_commands.Choice]:
    """Propose des complétions pour les IDs d'applications de jeux."""
    games = await self.steam_service.search_game_by_name(current) if current else self.steam_service.get_popular_games()
    return [
      app_commands.Choice(name=game.get('name')[:100], value=str(game.get('appid')))
      for game in games
    ][:25] if games else []

  @app_commands.command(name='nx_follow', description='placeholder')
  @app_commands.autocomplete(game=game_app_id_autocomplete)
  @app_commands.checks.has_permissions(administrator=True)
  async def follow(self, interaction: discord.Interaction, game: str, channel: discord.TextChannel) -> None:
    """Permet de suivre un jeu spécifique."""
    await interaction.response.defer(ephemeral=True, thinking=True)
    guild_id = interaction.guild.id
    locale = await self.guild_service.find_guild_locale(guild_id)
    game_exist = await self.game_service.find_game_for_guild(game, guild_id)
    if game_exist:
      await interaction.followup.send(self.bot.i18n.translate("cogs.game.commands.nx_follow.messages.exist", locale, game_name=game_exist.name, channel=game_exist.channel))
      return

    game_found = await self.steam_service.get_game_name(game)
    if not game_found:
      await interaction.followup.send(self.bot.i18n.translate("cogs.game.commands.nx_follow.messages.not_found", locale))
      return
    
    new_game = await self.game_service.add_game(game, interaction.guild.id, channel.id, game_found)
    await interaction.followup.send(self.bot.i18n.translate("cogs.game.commands.nx_follow.messages.success", locale, game_name=new_game.name, channel=new_game.channel))

  @app_commands.command(name='nx_unfollow', description='placeholder')
  @app_commands.autocomplete(game=game_name_autocomplete)
  @app_commands.checks.has_permissions(administrator=True)
  async def unfollow_game(self, interaction: discord.Interaction, game: str) -> None:
    """Permet d'arrêter de suivre un jeu spécifique."""
    await interaction.response.defer(ephemeral=True, thinking=True)
    guild_id = interaction.guild.id
    locale = await self.guild_service.find_guild_locale(guild_id)
    game_followed = await self.game_service.delete_game(game, guild_id)
    if not game_followed:
      await interaction.followup.send(self.bot.i18n.translate("cogs.game.commands.nx_unfollow.messages.not_followed", locale))
      return
    
    await interaction.followup.send(self.bot.i18n.translate("cogs.game.commands.nx_unfollow.messages.success", locale, game_name=game_followed.name, channel=game_followed.channel))

  @app_commands.command(name='nx_publish', description='placeholder')
  @app_commands.autocomplete(game=game_name_autocomplete)
  @app_commands.checks.has_permissions(administrator=True)
  async def publish_news(self, interaction: discord.Interaction, game: str) -> None:
    """Publie les dernières nouvelles d'un jeu suivi."""
    await interaction.response.defer(ephemeral=True, thinking=True)
    guild_id = interaction.guild.id
    locale = await self.guild_service.find_guild_locale(guild_id)
    game_exist = await self.game_service.find_game_for_guild(game, guild_id)
    if not game_exist:
      await interaction.followup.send(self.bot.i18n.translate("cogs.game.commands.nx_publish.messages.not_exist", locale, game_name=game))
      return

    news_found = await self.news_service.send_last_news(game_exist)
    if not news_found:
      await interaction.followup.send(self.bot.i18n.translate("cogs.game.commands.nx_publish.messages.not_found", locale, game_name=game_exist.name))
      return
    
    await interaction.followup.send(self.bot.i18n.translate("cogs.game.commands.nx_publish.messages.success", locale, game_name=game_exist.name, channel=game_exist.channel))

  @app_commands.command(name='nx_list', description='placeholder')
  @app_commands.checks.has_permissions(administrator=True)
  async def list_games(self, interaction: discord.Interaction) -> None:
    """Liste tous les jeux suivis pour le serveur."""
    await interaction.response.defer(ephemeral=True, thinking=True)
    guild_id = interaction.guild.id
    locale = await self.guild_service.find_guild_locale(guild_id)
    games_followed = await self.game_service.find_games_for_guild(guild_id)
    if not games_followed:
      await interaction.followup.send(self.bot.i18n.translate("cogs.game.commands.nx_list.messages.not_followed", locale))
      return
    
    await interaction.followup.send(''.join([self.bot.i18n.translate("cogs.game.commands.nx_list.messages.success", locale, game_name=game.name, app_id=game.id, channel=game.channel) for game in games_followed]))

  @app_commands.command(name='nx_reset', description='placeholder')
  @app_commands.checks.has_permissions(administrator=True)
  async def reset_games(self, interaction: discord.Interaction) -> None:
    """Réinitialise la liste des jeux suivis pour le serveur."""
    await interaction.response.defer(ephemeral=True, thinking=True)
    guild_id = interaction.guild.id
    locale = await self.guild_service.find_guild_locale(guild_id)
    games_followed = await self.game_service.delete_games(guild_id)
    if not games_followed:
      await interaction.followup.send(self.bot.i18n.translate("cogs.game.commands.nx_reset.messages.not_followed", locale))
      return
    
    await interaction.followup.send(self.bot.i18n.translate("cogs.game.commands.nx_reset.messages.success", locale, games=games_followed))

async def setup(bot: DiscordBot) -> None:
  """Configure le cog de jeux avec le bot."""
  await bot.add_cog(GameCog(bot))
