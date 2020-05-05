import re
import datetime
import traceback

import aiohttp
import pytz
import discord
from discord.ext import commands

import utilities as util

class Timetable(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        
    async def cog_command_error(self, ctx, error):
        if ctx.command in (self.bot.get_command('yesterday'), 
                           self.bot.get_command('tomorrow'),
                           self.bot.get_command('today')):
            if isinstance(error, commands.CommandInvokeError):
                embed = discord.Embed(title='This command can only be used on weekdays.',
                                      description=f'Usage: `>{ctx.command.name} {ctx.command.signature}`',
                                      timestamp=datetime.datetime.now(tz=pytz.timezone('Australia/NSW')),    
                                      colour=discord.Colour.from_rgb(255, 85, 85))
                await ctx.send(embed=embed)     

        if isinstance(error, (commands.MissingRequiredArgument, commands.BadArgument)):
            embed = discord.Embed(title='Student not found.',
                                  description=f'Usage: `>{ctx.command.name} {ctx.command.signature}`',
                                  timestamp=datetime.datetime.now(tz=pytz.timezone('Australia/NSW')),    
                                  colour=discord.Colour.from_rgb(255, 85, 85))
            await ctx.send(embed=embed)   

        elif isinstance(error, commands.CommandOnCooldown):
            embed = discord.Embed(title='Cooldown Reached',
                                  description=f'Please retry in `{error.retry_after}`.\n*stop trying to frick my bot pls*',
                                  timestamp=datetime.datetime.now(tz=pytz.timezone('Australia/NSW')),    
                                  colour=discord.Colour.from_rgb(255, 85, 85))
            await ctx.send(embed=embed)   

        else:
            traceback.print_exc()

    @commands.command(help='Attaches identity as a role, makes the "query" argument optional.')
    async def identify(self, ctx, *, query):
        identity = util.get_identity(ctx)
        if identity:
            name = identity[0].split('|')[0]
            embed = discord.Embed(title='Cannot assign role.',
                                  description=f'{ctx.author.mention} already identified as "{name}".',
                                  timestamp=datetime.datetime.now(tz=pytz.timezone('Australia/NSW')),    
                                  colour=discord.Colour.from_rgb(255, 85, 85))
            await ctx.send(embed=embed)
            return

        async with aiohttp.ClientSession() as session:
            student_info = await util.query_student_info(session, query)

        title = student_info['title'].split(' - ')[0]
        student_id = str(student_info['id'])        

        role = await ctx.guild.create_role(name=f"{title}|{student_id}")
        await ctx.author.add_roles(role)

        embed = discord.Embed(title='Assigned role.',
                  description=f'{ctx.author.mention} identified as "{title}"',
                  timestamp=datetime.datetime.now(tz=pytz.timezone('Australia/NSW')),    
                  colour=discord.Colour.from_rgb(80, 250, 123))
        await ctx.send(embed=embed)

    @commands.cooldown(1, 10, commands.BucketType.member)
    @commands.command(help="Displays the current class.")
    async def now(self, ctx, *, query=None):
        async with aiohttp.ClientSession() as session:
            student_info = await util.find_student_info(ctx, session, query)

            timetable_html = await util.fetch_timetable(session, student_info['id'])

            current_class = util.find_current_class(timetable_html)

        if current_class:
            period = current_class['period'].text[1:]
            title = current_class['info']['title'] 
            info = util.format_description(current_class['info']['description'])

            embed = discord.Embed(title=f"Showing Current Class for \"{student_info['title']}\":",
                                  timestamp=datetime.datetime.now(tz=pytz.timezone('Australia/NSW')),    
                                  colour=discord.Colour.from_rgb(80, 250, 123)
            ).add_field(name=f"Period {period}", value=f'**{title}**\n{info}', inline=False)
            
            await ctx.send(embed=embed)

        else:
            embed = discord.Embed(title=f"No timetabled class currently for \"{student_info['title']}\":",
                  timestamp=datetime.datetime.now(tz=pytz.timezone('Australia/NSW')),    
                  colour=discord.Colour.from_rgb(80, 250, 123))
            await ctx.send(embed=embed)
            
    @commands.cooldown(1, 10, commands.BucketType.member)
    @commands.command(help="Displays the next class.")
    async def next(self, ctx, *, query=None):
        async with aiohttp.ClientSession() as session:
            student_info = await util.find_student_info(ctx, session, query)
            timetable_html = await util.fetch_timetable(session, student_info['id'])
            next_class = util.find_next_class(timetable_html)

        if next_class:
            period = next_class['period'].text[1:]
            title = next_class['info']['title'] 
            info = util.format_description(next_class['info']['description'])

            embed = discord.Embed(title=f"Showing Next Class for \"{student_info['title']}\":",
                                  timestamp=datetime.datetime.now(tz=pytz.timezone('Australia/NSW')),    
                                  colour=discord.Colour.from_rgb(80, 250, 123)
            ).add_field(name=f"Period {period}", value=f'**{title}**\n{info}', inline=False)
            
            await ctx.send(embed=embed)

        else:
            embed = discord.Embed(title=f"No timetabled class next period for \"{student_info['title']}\":",
                  timestamp=datetime.datetime.now(tz=pytz.timezone('Australia/NSW')),    
                  colour=discord.Colour.from_rgb(80, 250, 123))
            await ctx.send(embed=embed)

    @commands.cooldown(1, 10, commands.BucketType.member)
    @commands.command(help="Displays the classes of today. \nCan only be used on weekdays.")
    async def today(self, ctx, *, query = None):
        async with aiohttp.ClientSession() as session:
            student_info = await util.find_student_info(ctx, session, query)   

            timetable_html = await util.fetch_timetable(session, student_info['id'])

            week, day = util.find_date(timetable_html)

        await ctx.invoke(self.bot.get_command('timetable'), week, day.name, query=query)

    @commands.cooldown(1, 10, commands.BucketType.member)
    @commands.command(help="Displays the classes of tomorrow. \nCan only be used on weekdays.")
    async def tomorrow(self, ctx, *, query = None):
        async with aiohttp.ClientSession() as session:
            student_info = await util.find_student_info(ctx, session, query)   

            timetable_html = await util.fetch_timetable(session, student_info['id'])

            week, day = util.find_date(timetable_html)
            week, day = util.next_date(week, day)

        await ctx.invoke(self.bot.get_command('timetable'), week, day.name, query=query)


    @commands.cooldown(1, 10, commands.BucketType.member)
    @commands.command(help="Displays the classes of yesterday. \nCan only be used on weekdays.")
    async def yesterday(self, ctx, *, query = None):
        async with aiohttp.ClientSession() as session:
            student_info = await util.find_student_info(ctx, session, query)   

            timetable_html = await util.fetch_timetable(session, student_info['id'])

            week, day = util.find_date(timetable_html)
            week, day = util.prev_date(week, day)

        await ctx.invoke(self.bot.get_command('timetable'), week, day.name, query=query)

    @commands.cooldown(1, 10, commands.BucketType.member)
    @commands.command(help="Displays the classes of a specific day. \nWeek can only take the values of 'a' or 'b', and day_of_week must be a weekday.")
    async def timetable(self, ctx, week, day_of_week, *, query = None):
        day_index = util.SchoolDays[day_of_week.upper()].value

        async with aiohttp.ClientSession() as session:
            student_info = await util.find_student_info(ctx, session, query)   

            timetable_html = await util.fetch_timetable(session, student_info['id'])

            day_classes = util.find_day_classes(week.lower(), day_index, timetable_html)

        if day_classes:
            embed = discord.Embed(title=f"Showing Classes for \"{student_info['title']}\" on {day_of_week.upper()}, Week {week.upper()}:",
                                  timestamp=datetime.datetime.now(tz=pytz.timezone('Australia/NSW')),    
                                  colour=discord.Colour.from_rgb(80, 250, 123))
            for day_class in day_classes:
                period = day_class['period'][2:]
                title = day_class['info']['title'] 
                info = util.format_description(day_class['info']['description'])

                embed.add_field(name=f"Period {period}", value=f'**{title}**\n{info}', inline=False)
        else: 
            embed = discord.Embed(title=f"No periods on {day_of_week.upper()}, Week {week.upper()} for \"{student_info['title']}\".",
                                  timestamp=datetime.datetime.now(tz=pytz.timezone('Australia/NSW')),    
                                  colour=discord.Colour.from_rgb(80, 250, 123))
    
        await ctx.send(embed=embed)

    @commands.cooldown(1, 10, commands.BucketType.member)
    @commands.command(help="Displays the current week (a or b) and the weekday.")
    async def date(self, ctx, *, query = None):
        async with aiohttp.ClientSession() as session:
            student_info = await util.find_student_info(ctx, session, query)   

            timetable_html = await util.fetch_timetable(session, student_info['id'])

            week, day = util.find_date(timetable_html)

        embed = discord.Embed(title=f"Today's date is {day.name.upper()}, Week {week.upper()}",
                              timestamp=datetime.datetime.now(tz=pytz.timezone('Australia/NSW')),    
                              colour=discord.Colour.from_rgb(80, 250, 123))
        await ctx.send(embed=embed)

def setup(bot):
    bot.add_cog(Timetable(bot))