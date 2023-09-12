import discord
from discord import app_commands
import config

intents = discord.Intents.default()
client = discord.Client(intents=intents)
tree = app_commands.CommandTree(client)

@client.event
async def on_ready():
    print(f'We have logged in as {client.user}')

@client.event
async def on_guild_join(guild):
    general_channel = discord.utils.get(guild.text_channels, name='general')
    if general_channel:
        await general_channel.send('Hey! Set a channel for the games using `/setgame`')

@tree.command(name="setgame", description="Set the channel for games")
async def setgame(ctx):
    await ctx.send("This is a test")
    pass 


client.run(config.TOKEN)
