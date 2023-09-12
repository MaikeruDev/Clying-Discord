from utils.database import get_game_channel
from global_vars import active_lobbies

def check_game_channel(ctx):
    guild_id = ctx.guild.id
    channel_id = ctx.channel.id

    game_channel_id = get_game_channel(guild_id)
    
    return channel_id == game_channel_id 

def get_lobby(guild_id): 
    return active_lobbies.get(guild_id) or None