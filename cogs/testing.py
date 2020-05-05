import re

import aiohttp
import discord
from bs4 import BeautifulSoup
from discord.ext import commands

import utilities as util

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

    @commands.command()
    async def query(self, ctx, identity: int):
        row = await self.bot.database.query_public_tasks(identity)
        await ctx.send(f'{row["id"]} : `{row["author"]}` "{row["description"]}"')

    @commands.command()
    async def create_task(self, ctx, *, description):
        table = await self.bot.database.enter_public_task(ctx.author.id, description)
       
    @commands.command()
    async def get_table(self, ctx):
        table = await self.bot.database.get_public_tasks()
        

def setup(bot):
    bot.add_cog(Testing(bot))