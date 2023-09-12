from utils.helpers import check_game_channel, get_lobby
from utils.database import get_game_channel
import random

async def start_game(guild_id, client, tree):
    
    lobby = get_lobby(guild_id)

    if not lobby:
        return

    game_channel_id = get_game_channel(guild_id)
    game_channel = client.get_channel(game_channel_id)

    spy = random.randint(0, len(lobby["players"])-1)
    for i in range(len(lobby["players"])):
        if i == spy:
            await lobby["players"][i].send("You are the spy!")
        else:
            await lobby["players"][i].send("You are not the spy!")
            
    await game_channel.send("The game has started! Check your DMs for your image!")
