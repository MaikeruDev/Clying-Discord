import asyncio
import discord
from discord import app_commands
from discord import Embed
from utils.helpers import check_game_channel, get_lobby
from game_handler import start_game

from global_vars import active_lobbies

def setup_game_commands(client, tree): 

    @tree.command(name="creategame", description="Create a new game lobby", guild=discord.Object(id=1151074499614224447))
    async def creategame(ctx):
        if not check_game_channel(ctx):
            await ctx.response.send_message("You can only use this command in the designated game channel.")
            return

        guild_id = ctx.guild.id
        creator = ctx.user

        if guild_id in active_lobbies:
            await ctx.response.send_message("🔹 A game is already active in this server.")
            return

        active_lobbies[guild_id] = {
            "creator": creator,
            "players": [creator],
        }
        await ctx.response.send_message(
    f"🎉 **Game Lobby Opened!** 🎉\n\n"
    f"🎮 **Created by:** {creator.mention}\n"
    f"🔑 **How to Join:** Use `/join` to become a part of the excitement!\n"
    f"🚀 **How to Start:** The game begins when the creator initiates `/startgame`.\n\n"
    f"Get ready for a thrilling adventure! Gather your friends and let the fun begin! 💫"
) 
        
    @tree.command(name="join", description="Join an existing game lobby", guild=discord.Object(id=1151074499614224447))
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

        active_lobbies[guild_id]["players"].append(player)
        await ctx.response.send_message(f"🔹 {player.mention} has joined the game lobby.") 

    @tree.command(name="closegame", description="Close the currently active game", guild=discord.Object(id=1151074499614224447))
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
 
    @tree.command(name="leave", description="Leave the currently active game", guild=discord.Object(id=1151074499614224447))
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
        
        #add an if statement to check if the player that leaves is the host. if so and he is the last player, close the game. if there are still other players make them the host
        if player == active_lobbies[guild_id]["creator"]:
            if len(active_lobbies[guild_id]["players"]) == 1:
                del active_lobbies[guild_id]
                await ctx.response.send_message(f"🔹 The game created by {player.mention} has been closed.")
                return
            else:
                active_lobbies[guild_id]["creator"] = active_lobbies[guild_id]["players"][1]
                await ctx.response.send_message(f"🔹 {player.mention} has left the game lobby. {active_lobbies[guild_id]['creator'].mention} is now the host.")
                active_lobbies[guild_id]["players"].remove(player)
                return
        
        active_lobbies[guild_id]["players"].remove(player)
        await ctx.response.send_message(f"🔹 {player.mention} has left the game lobby.")


    @tree.command(name="startgame", description="Start the game with the current lobby", guild=discord.Object(id=1151074499614224447))
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
         
        if len(lobby["players"]) < 2:
            await ctx.response.send_message("🔹 You need at least 2 players to start the game.")
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
 
        await asyncio.sleep(2)

 
        await start_game(ctx.guild.id, client, tree)
