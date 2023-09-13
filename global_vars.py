active_lobbies = {}

import discord
from discord import app_commands

intents = discord.Intents.default()
intents.members = True
intents.guilds = True
intents.voice_states = True
intents.messages = True
 
client = discord.Client(intents=intents)
tree = app_commands.CommandTree(client)