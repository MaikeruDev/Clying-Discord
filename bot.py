import discord
from discord.ext import commands
import config

intents = discord.Intents.default()
bot = commands.Bot(command_prefix="!", intents=intents)

@bot.event
async def on_ready():
    print(f"We have logged in as {bot.user}")

@bot.command()
async def set_game_channel(ctx, channel: discord.TextChannel):
    config.GAME_CHANNEL_ID = channel.id
    await ctx.send(f"Game channel set to: {channel.name}")

@bot.command()
async def game_channel(ctx):
    if config.GAME_CHANNEL_ID:
        channel = bot.get_channel(config.GAME_CHANNEL_ID)
        await ctx.send(f"The game channel is: {channel.name}")
    else:
        await ctx.send("The game channel is not set.")

bot.run(config.TOKEN)
