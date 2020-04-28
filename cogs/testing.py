import discord
from discord.ext import commands

class Testing(commands.Cog):
    def __init__(self,bot):
        self.bot = bot

    @commands.command()
    async def force(self, ctx, *, forced_class):
        self.bot.current_class = forced_class
        await ctx.send("Success.")

def setup(bot):
    bot.add_cog(Testing(bot))