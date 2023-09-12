from discord.ext import commands

class GameCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command()
    async def start_game(self, ctx):
        if ctx.channel.id == self.bot.config.GAME_CHANNEL_ID:
            await ctx.send("Starting the game...")
        else:
            await ctx.send("This is not the game channel.")

def setup(bot):
    bot.add_cog(GameCog(bot))
