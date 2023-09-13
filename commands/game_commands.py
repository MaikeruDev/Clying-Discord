import asyncio
import discord
import logging
from discord import app_commands
from discord import Embed
from utils.helpers import check_game_channel, get_lobby
from utils.database import get_game_channel
from game_handler import start_game 
from global_vars import client, tree, active_lobbies 

def setup_game_commands(): 

    @tree.command(name="creategame", description="Create a new game lobby")
    async def creategame(ctx):
        if not check_game_channel(ctx):
            await ctx.response.send_message("You can only use this command in the designated game channel.")
            return

        guild_id = ctx.guild.id
        creator = ctx.user

        if guild_id in active_lobbies:
            await ctx.response.send_message("🔹 A game is already active in this server.")
            return
        
        logging.info(f"Game lobby created by {creator.name} in {ctx.guild.name} (ID: {ctx.guild.id})")

        active_lobbies[guild_id] = {
            "creator": creator,
            "players": [creator],
            "current_player": -1,
        }
        await ctx.response.send_message(
    f"🎉 **Game Lobby Opened!** 🎉\n\n"
    f"🎮 **Created by:** {creator.mention}\n"
    f"🔑 **How to Join:** Use `/join` to become a part of the excitement!\n"
    f"🚀 **How to Start:** The game begins when the creator initiates `/startgame`.\n\n"
    f"Get ready for a thrilling adventure! Gather your friends and let the fun begin! 💫"
) 
        
    @tree.command(name="join", description="Join an existing game lobby")
    async def join(ctx):
        if not check_game_channel(ctx):
            await ctx.response.send_message("🔹 You can only use this command in the designated game channel.")
            return

        guild_id = ctx.guild.id
        player = ctx.user

        if guild_id not in active_lobbies:
            await ctx.response.send_message(f"🔹 No active game lobby found in this server.")
            return

        if player in active_lobbies[guild_id]["players"]:
            await ctx.response.send_message(f"🔹 You have already joined the game lobby.")
            return
 
        if len(active_lobbies[guild_id]["players"]) >= 10:
            await ctx.response.send_message(f"🔹 The game lobby is full.")
            return

        active_lobbies[guild_id]["players"].append(player)
        await ctx.response.send_message(f"🔹 {player.mention} has joined the game lobby.") 

    @tree.command(name="closegame", description="Close the currently active game")
    async def closegame(ctx): 
        if not check_game_channel(ctx):
            await ctx.response.send_message("🔹 You can only use this command in the designated game channel.")
            return
        
        guild_id = ctx.guild.id
 
        if active_lobbies.get(guild_id): 
            game_creator = active_lobbies[guild_id]['creator']
 
            if ctx.user == game_creator or ctx.user.guild_permissions.administrator: 
                del active_lobbies[guild_id]
                await ctx.response.send_message(f"🔹 The game created by {game_creator.name} has been closed.")
            else:
                await ctx.response.send_message("🔹 You do not have the necessary permissions to close this game.")
        else:
            await ctx.response.send_message("🔹 No active game found in this server.")
 
    @tree.command(name="leave", description="Leave the currently active game")
    async def leave(ctx): 
        if not check_game_channel(ctx):
            await ctx.response.send_message("🔹 You can only use this command in the designated game channel.")
            return
        
        guild_id = ctx.guild.id
        player = ctx.user

        if guild_id not in active_lobbies:
            await ctx.response.send_message("🔹 No active game lobby found in this server.")
            return
        
        if player not in active_lobbies[guild_id]["players"]:
            await ctx.response.send_message("🔹 You have not joined the game lobby.")
            return
         
        if player == active_lobbies[guild_id]["creator"]:
            if len(active_lobbies[guild_id]["players"]) == 1:
                del active_lobbies[guild_id]
                await ctx.response.send_message(f"🔹 The game created by {player.mention} has been closed due to not enough players.")
                return
            else:
                active_lobbies[guild_id]["creator"] = active_lobbies[guild_id]["players"][1]
                await ctx.response.send_message(f"🔹 {player.mention} has left the game lobby. {active_lobbies[guild_id]['creator'].mention} is now the host.")
                active_lobbies[guild_id]["players"].remove(player)
                return
        
        active_lobbies[guild_id]["players"].remove(player)
        await ctx.response.send_message(f"🔹 {player.mention} has left the game lobby.")
  

    @tree.command(name="startgame", description="Start the game with the current lobby")
    async def startgame(ctx):
        if not check_game_channel(ctx):
            await ctx.response.send_message("🔹 You can only use this command in the designated game channel.")
            return
         
        lobby = get_lobby(ctx.guild.id)
 
        if not lobby:
            await ctx.response.send_message("🔹 No active game lobby found in this server.")
            return
         
        if ctx.user not in lobby["players"]:
            await ctx.response.send_message("🔹 You have not joined the game lobby.")
            return
          
        if ctx.user != lobby["creator"]: 
            await ctx.response.send_message("🔹 You are not the host of this game.") 
            return
         
        if len(lobby["players"]) < 3:
            await ctx.response.send_message("🔹 You need at least 3 players to start the game.")
            return
 
        player_mentions = [player.mention for player in lobby["players"]]

        embed = Embed(
            title="🎮 Game Lobby",
            description="Prepare yourself for an electrifying game session! Lie, analyze, strategize and be the best!",
            color=0x4CAF50,
        )

        embed.set_thumbnail(url="https://placehold.co/600x300/png")  
        embed.add_field(name="👑 Host", value=lobby["creator"].mention, inline=False)
        embed.add_field(name="🎮 Players", value="\n".join(player_mentions), inline=False)
        embed.add_field(name="⏳ Start Time", value="Starting in a few moments...", inline=False)
        embed.set_footer(text="Make sure to follow the game rules and have fun! 🙂")  

        await ctx.response.send_message(embed=embed) 

        lobby["started"] = True
 
        await start_game(ctx.guild.id)

        game_channel_id = get_game_channel(ctx.guild.id)
        game_channel = client.get_channel(game_channel_id)

        await game_channel.send("🔹 Do you want to play again?")
        await game_channel.send("🔹 Type `/playagain` to play again or `/closegame` to close the lobby.")
        await asyncio.sleep(300)
        if ctx.response.is_done():
            return
        else:
            await game_channel.send("🔹 No response received. The game lobby has been closed.")
            del active_lobbies[ctx.guild.id]
            return
        
    @tree.command(name="playagain", description="Play the game again")
    async def playagain(ctx):
        if not check_game_channel(ctx):
            await ctx.response.send_message("🔹 You can only use this command in the designated game channel.")
            return
         
        lobby = get_lobby(ctx.guild.id)
 
        if not lobby:
            await ctx.response.send_message("🔹 No active game lobby found in this server.")
            return
         
        if ctx.user not in lobby["players"]:
            await ctx.response.send_message("🔹 You have not joined the game lobby.")
            return
          
        if ctx.user != lobby["creator"]: 
            await ctx.response.send_message("🔹 You are not the host of this game.") 
            return
         
        if len(lobby["players"]) < 3:
            await ctx.response.send_message("🔹 You need at least 3 players to start the game.")
            return

        await ctx.response.send_message("🔹 The game will start in a few moments...")
        await asyncio.sleep(2)

        lobby["started"] = True
 
        await start_game(ctx.guild.id) 
        
        game_channel_id = get_game_channel(ctx.guild.id)
        game_channel = client.get_channel(game_channel_id)

        await game_channel.send("🔹 Do you want to play again?")
        await game_channel.send("🔹 Type `/playagain` to play again or `/closegame` to close the lobby.")
        await asyncio.sleep(300)
        if ctx.response.is_done():
            return
        else:
            await game_channel.send("🔹 No response received. The game lobby has been closed.")
            del active_lobbies[ctx.guild.id]
            return