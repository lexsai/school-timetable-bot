import discord
from discord.ext import commands

class Testing(commands.Cog):
    def __init__(self,bot):
        self.bot = bot

    async def cog_check(self, ctx):	
        return await ctx.bot.is_owner(ctx.author)

    @commands.command()
    async def purge_roles(self, ctx):
    	for role in ctx.guild.roles:
    		if not role.members:
    			await role.delete()

    @commands.command()
    async def force(self, ctx, *, forced_class):
        self.bot.current_class = forced_class
        await ctx.send("Success.")

def setup(bot):
    bot.add_cog(Testing(bot))