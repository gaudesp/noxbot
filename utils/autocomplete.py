# utils/autocomplete.py
import discord
from discord import app_commands
from repositories import game_repository
from services.steam_api import search_game_by_name

async def game_name_autocomplete(interaction: discord.Interaction, current: str):
  games = game_repository.get_games_for_guild(interaction.guild.id)
  matching_games = [game for game in games if current.lower() in game.game_name.lower()]
  return [
    app_commands.Choice(name=game.game_name, value=str(game.app_id))
    for game in matching_games[:25]
  ]

async def game_app_id_autocomplete(interaction: discord.Interaction, current: str):
  if not current:
    return []
  matching_games = await search_game_by_name(current)
  return [
    app_commands.Choice(name=game['name'], value=str(game['appid']))
    for game in matching_games
  ]
