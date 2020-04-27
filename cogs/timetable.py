import datetime
import traceback

import aiohttp
import pytz
import discord
from discord.ext import commands

import custom_classes as cc

class Timetable(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command()
    async def identify(self, ctx, *, query):
        async with aiohttp.ClientSession() as session:
            student_info = await cc.query_student_info(session, query)

        title = student_info['title']
        student_id = str(student_info['id'])
        
        if f"{title.split(' - ')[0]}|{student_id}" in [role.name for role in ctx.author.roles]:
            embed = discord.Embed(title='Cannot assign role.',
                                  description=f'{ctx.author.mention} already identified as "{title}"',
                                  timestamp=datetime.datetime.now(tz=pytz.timezone('Australia/NSW')),    
                                  colour=discord.Colour.from_rgb(255, 85, 85))
            await ctx.send(embed=embed)
        else:
            role = await ctx.guild.create_role(name=f"{title.split(' - ')[0]}|{student_id}")
            await ctx.author.add_roles(role)

            embed = discord.Embed(title='Assigned role.',
                      description=f'{ctx.author.mention} identified as "{title}"',
                      timestamp=datetime.datetime.now(tz=pytz.timezone('Australia/NSW')),    
                      colour=discord.Colour.from_rgb(80, 250, 123))
            await ctx.send(embed=embed)

    @identify.error
    async def identify_error(self, ctx, error):
        if isinstance(error, commands.MissingRequiredArgument) or isinstance(error, commands.BadArgument):
            embed = discord.Embed(title='Student not found.',
                                  description='Usage: `>identify <name of student>`',
                                  timestamp=datetime.datetime.now(tz=pytz.timezone('Australia/NSW')),    
                                  colour=discord.Colour.from_rgb(255, 85, 85))
            await ctx.send(embed=embed)

        else: 
            traceback.print_exc()

    @commands.command()
    async def now(self, ctx, *, query=None):
        async with aiohttp.ClientSession() as session:
            student_info = await cc.find_student_info(ctx, session, query)

            timetable_html = await cc.fetch_timetable(session, student_info['id'])

            current_class = await cc.parse_current_class(timetable_html)

        if current_class == None:
            embed = discord.Embed(title=f"No timetabled class currently for \"{student_info['title']}\":",
                  timestamp=datetime.datetime.now(tz=pytz.timezone('Australia/NSW')),    
                  colour=discord.Colour.from_rgb(80, 250, 123))
            await ctx.send(embed=embed)
            return

        title = current_class['title'] 
        info = '\n'.join([line.strip() for line in current_class['info'].split('\n') if line.strip() != ''])

        embed = discord.Embed(title=f"Showing Current Class for \"{student_info['title']}\":",
                              description=f'**{title}**\n{info}',
                              timestamp=datetime.datetime.now(tz=pytz.timezone('Australia/NSW')),    
                              colour=discord.Colour.from_rgb(80, 250, 123))
        await ctx.send(embed=embed)

    @now.error
    async def now_error(self, ctx, error):
        if isinstance(error, commands.MissingRequiredArgument) or isinstance(error, commands.BadArgument):
            embed = discord.Embed(title='Student not found.',
                                  description='Usage: `>now <name of student>`',
                                  timestamp=datetime.datetime.now(tz=pytz.timezone('Australia/NSW')),    
                                  colour=discord.Colour.from_rgb(255, 85, 85))
            await ctx.send(embed=embed)

        else: 
            traceback.print_exc()

    @commands.command()
    async def timetable(self, ctx, *, query = None):
        async with aiohttp.ClientSession() as session:
            student_info = await cc.find_student_info(ctx, session, query)   

            timetable_html = await cc.fetch_timetable(session, student_info['id'])

            today_classes = await cc.parse_today_classes(timetable_html)

        if not today_classes == []:
            embed = discord.Embed(title=f"Showing Today's Classes for \"{student_info['title']}\":",
                                  timestamp=datetime.datetime.now(tz=pytz.timezone('Australia/NSW')),    
                                  colour=discord.Colour.from_rgb(80, 250, 123))
            for today_class in today_classes:
                title = today_class['title'] 
                info = '\n'.join([line.strip() for line in today_class['info'].split('\n') if line.strip() != ''])

                embed.add_field(name=f'Period {today_classes.index(today_class)+1}', value=f'**{title}**\n{info}', inline=False)
        else: 
            embed = discord.Embed(title=f"No periods today for \"{student_info['title']}\".",
                                  timestamp=datetime.datetime.now(tz=pytz.timezone('Australia/NSW')),    
                                  colour=discord.Colour.from_rgb(80, 250, 123))
    
        await ctx.send(embed=embed)

    @timetable.error
    async def timetable_error(self, ctx, error):
        if isinstance(error, commands.MissingRequiredArgument) or isinstance(error, commands.BadArgument):
            embed = discord.Embed(title='Student not found.',
                                  description='Usage: `>timetable <name of student>`',
                                  timestamp=datetime.datetime.now(tz=pytz.timezone('Australia/NSW')),    
                                  colour=discord.Colour.from_rgb(255, 85, 85))
            await ctx.send(embed=embed)

        else: 
            traceback.print_exc()


def setup(bot):
    bot.add_cog(Timetable(bot))
    