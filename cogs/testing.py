import re

import aiohttp
import discord
from bs4 import BeautifulSoup
from discord.ext import commands

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

    @commands.command()
    async def test(self, ctx, *, query = None):
        async with aiohttp.ClientSession() as session:
            student_info = await cc.find_student_info(ctx, session, query)   

            timetable_html = await cc.fetch_timetable(session, student_info['id'])

            periods = cc.parse_period_classes(timetable_html)

        for period, classes in periods.items():
            for _class in classes:
                try:
                    if 'today' in _class['class']:
                        print(_class.find('div', {'class' : 'timetable-class'}))
                except TypeError:
                    pass

def setup(bot):
    bot.add_cog(Testing(bot))