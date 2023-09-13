import asyncio
import time
from utils.helpers import check_game_channel, get_lobby
from utils.database import get_game_channel
from global_vars import client, tree 
import discord
import random
 

@tree.command(name="next", description="End your turn early", guild=discord.Object(id=1151074499614224447))
async def next(ctx):   
    
    if not check_game_channel(ctx):
        await ctx.response.send_message("🔹 You can only use this command in the designated game channel.")
        return
    
    guild_id = ctx.guild.id 
    player = ctx.user

    lobby = get_lobby(guild_id)

    if not lobby:
        await ctx.response.send_message("🔹 No active game lobby found in this server.")
        return
    
    if player not in lobby["players"]:
        await ctx.response.send_message("🔹 You have not joined the game lobby.")
        return
        
    if lobby["current_player"] == -1:
        await ctx.response.send_message("🔹 The game has not started yet.")
        return
        
    if lobby["current_player"] != player:
        await ctx.response.send_message("🔹 It is not your turn.")
        return  
    
    await ctx.response.send_message("🔹 Ended turn early")
    return
     

async def start_game(guild_id):  

    await asyncio.sleep(2)

    lobby = get_lobby(guild_id)

    if not lobby:
        return

    lobby["current_player"] = -1

    game_channel_id = get_game_channel(guild_id)
    game_channel = client.get_channel(game_channel_id)

    spy = random.randint(0, len(lobby["players"])-1)

    for i in range(len(lobby["players"])):
        if i == spy: 
            embed = discord.Embed(
                title="You are the liar!",
                description="You have to come up with an imaginary picture!",
                color=0xff0000,
            )
            embed.set_image(url="https://media.discordapp.net/attachments/1097279128312484042/1151150114698694697/maikeru.dev_an_image_of_a_person_in_a_black_cloak_from_a_poker__4abb1c99-b971-4c9c-80b6-238fe4aaae45.png?width=936&height=936")

        else:
            timestamp = int(time.time())

            # Create the URL with the timestamp as a query parameter
            image_url = f"https://random.imagecdn.app/1920/1800?timestamp={timestamp}"
            
            embed = discord.Embed(
                title="You are not the liar!",
                description="You have to explain your picture to the others!",
                color=0x4CAF50,
            )
            embed.set_image(url=image_url)

        await lobby["players"][i].send(embed=embed)

    started_embed = discord.Embed(
        title="Game started!",
        description="Check your DM's to see which role you got. I will announce the first player in 10 seconds.",
        color=0x0335fc,
    )

    await game_channel.send(embed=started_embed)

    await asyncio.sleep(10)

    for i in range(len(lobby["players"])):
        lobby["current_player"] = lobby["players"][i]
        embed = discord.Embed(
            title="It's your turn.",
            description="Explain your picture to the others! \n Press `/next` to end your turn early.",
            color=0x0335fc,
        )

        await lobby["players"][i].send(embed=embed)

        await game_channel.send(f"🔹 {lobby['players'][i].mention} is now explaining their picture. The others have 30 seconds to ask questions. \n Type `/next` to end your turn early.")

        def is_valid_next_command(message):
            return message.content == "🔹 Ended turn early" and message.author.id == 1151068827686285312

        try:
            message = await client.wait_for('message', check=is_valid_next_command, timeout=30.0)
        except asyncio.TimeoutError:
            await game_channel.send(f"🔹 {lobby['current_player'].mention} your turn is over.")

    lobby["current_player"] = -1

    await game_channel.send("🔹 The round is over. Get ready for voting.")
    await asyncio.sleep(5)

    poll_embed = discord.Embed(
        title="Vote for the liar!",
        description="React with the corresponding number to vote for the liar.",
        color=0xff0000,
    ) 
    
    for i, player in enumerate(lobby["players"], 1):
        poll_embed.add_field(name=f"Player {i}", value=player.mention, inline=True)
    
    poll_message = await game_channel.send(embed=poll_embed) 

    for i in range(1, len(lobby["players"]) + 1):
        await poll_message.add_reaction(f"{i}\N{combining enclosing keycap}")
    
    votes = {}

    def is_valid_reaction(reaction, user):
        if reaction.message.id != poll_message.id:
            return False
        
        if user not in lobby["players"]:
            return False
        
        valid_emojis = [f"{i}\N{combining enclosing keycap}" for i in range(1, len(lobby["players"]) + 1)]
        if reaction.emoji not in valid_emojis:
            return False
        
        if user in votes:
            return False
        
        vote_index = valid_emojis.index(reaction.emoji) + 1
        votes[user] = vote_index
        
        if len(votes) == len(lobby["players"]):
            return True
        
        return False
    
    try:
        reaction, user = await client.wait_for('reaction_add', check=is_valid_reaction, timeout=30.0) 
        await game_channel.send("🔹 Voting has ended. Votes.")
    except asyncio.TimeoutError:
        await game_channel.send("🔹 Voting has ended. Time.")
        return 
    
    vote_counts = {i: 0 for i in range(1, len(lobby["players"]) + 1)}
    for user_vote in votes.values():
        vote_counts[user_vote] += 1

    most_votes = max(vote_counts.values())
    most_voted_players = [player for player, votes_count in vote_counts.items() if votes_count == most_votes]

    embed = discord.Embed(
        title="Vote Results",
        description="Here are the vote counts for each player and the result:",
        color=0xff0000 if len(most_voted_players) > 1 else 0x4CAF50,
    )

    for i in range(1, len(lobby["players"]) + 1):
        player_id = lobby["players"][i - 1].id
        votes_count = vote_counts.get(i, 0)
        embed.add_field(
            name=f"Player {i}",
            value=f"<@{player_id}> has {votes_count} votes",
            inline=False,
        )

    if len(most_voted_players) > 1:
        embed.add_field(
            name="Result",
            value="There is a tie in the votes. The liar wins!",
            inline=False,
        )
    else:
        most_voted_player = lobby["players"][most_voted_players[0] - 1]
        if most_voted_player == lobby["players"][spy]:
            embed.add_field(
                name="Result",
                value="The liar has been successfully voted out! The civilians win!",
                inline=False,
            )
        else:
            embed.add_field(
                name="Result",
                value=f"{most_voted_player.mention} has been voted out, but they were not the liar. The liar wins!",
                inline=False,
            )

    await game_channel.send(embed=embed)

    votes.clear()

    await asyncio.sleep(5)

    return