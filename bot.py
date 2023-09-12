import config
import logging
from datetime import datetime
from utils.database import set_game, get_game_channel
from commands import game_commands 
import discord 
from discord import app_commands

intents = discord.Intents.default()
intents.members = True
intents.guilds = True
intents.voice_states = True
intents.messages = True
 
client = discord.Client(intents=intents)
tree = app_commands.CommandTree(client)

game_commands.setup_game_commands(client, tree)
 
""" now = datetime.now()
 
timestamp = now.strftime("%Y-%m-%d_%H-%M-%S")
 
logging.basicConfig(                                                                            For Final use only
    filename=f'logs/bot_log_{timestamp}.log',
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
) """
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')             # For testing only
 
@client.event
async def on_ready(): 
    logging.info(f"We have logged in as {client.user}")

    await tree.sync(guild=discord.Object(id=1151074499614224447)) 

@client.event
async def on_guild_join(guild): 
    channel = guild.system_channel
    if channel and channel.permissions_for(guild.me).send_messages:
        embed = discord.Embed(
            title="👋 Welcome to the Ultimate Gaming Experience!",
            description=(
                "Thank you for inviting me to your server! 🎉\n"
                "I am here to enhance your gaming sessions with fun and engaging group games.\n\n"
                "🛠️ **Setting Up Your Game Channel**\n"
                "To kick things off, set up a dedicated channel for all your gaming activities using the `/setgame` command. This will be the home for all the exciting games and challenges that await!\n\n"
                "📚 **Need Help?**\n"
                "If you encounter any issues or need assistance with setting up or using the bot, feel free to reach out to our support team.\n\n"
                "💡 **Ready to Play?**\n"
                "Once your game channel is set, gather your friends and get ready for a series of thrilling games designed to test your skills and foster camaraderie. Remember, it's all in good fun!\n\n"
                "Let's create unforgettable gaming moments together! 🌟"
            ),
            color=0x00FF00,
        )
        
        await channel.send(embed=embed)

        logging.info(f"Joined new guild: {guild.name} (ID: {guild.id})")

@tree.command(name="setgame", description="Set the channel for games", guild=discord.Object(id=1151074499614224447))
async def setgame(ctx):
    guild_id = ctx.guild.id
    channel_id = ctx.channel.id

    set_game(guild_id, channel_id)
    
    await ctx.response.send_message(f"The game channel has been set to <#{channel_id}>.")
    logging.info(f"Game channel set to {channel_id} for guild {guild_id}")
    pass  

client.run(config.TOKEN)
