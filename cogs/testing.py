import re

import aiohttp
import discord
from bs4 import BeautifulSoup
from discord.ext import commands
from discord.ext import menus

import custom_classes as cc

class Testing(commands.Cog):
    def __init__(self,bot):
        self.bot = bot

    async def cog_check(self, ctx): 
        return await ctx.bot.is_owner(ctx.author)

    @commands.command()
    async def prune_roles(self, ctx):
        pruned_roles = [role for role in ctx.guild.roles if not role.members]
        for role in pruned_roles:
            await role.delete()
        
        await ctx.send(f'Deleted {len(pruned_roles)} unused role(s).')

    @commands.command()
    async def force(self, ctx, *, forced_class):
        self.bot.current_class = forced_class
        await ctx.send("Success.")

def setup(bot):
    bot.add_cog(Testing(bot))