import re
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

    async def cog_command_error(self, ctx, error):
        if isinstance(error, (commands.MissingRequiredArgument, commands.BadArgument)):
            embed = discord.Embed(title='Student not found.',
                                  description=f'Usage: `>{ctx.command.name} <name of student>`',
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

    @commands.command()
    async def identify(self, ctx, *, query):
        identity = cc.get_identity(ctx)
        if identity:
            name = identity[0].split('|')[0]
            embed = discord.Embed(title='Cannot assign role.',
                                  description=f'{ctx.author.mention} already identified as "{name}".',
                                  timestamp=datetime.datetime.now(tz=pytz.timezone('Australia/NSW')),    
                                  colour=discord.Colour.from_rgb(255, 85, 85))
            await ctx.send(embed=embed)
            return

        async with aiohttp.ClientSession() as session:
            student_info = await cc.query_student_info(session, query)

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
    @commands.command()
    async def now(self, ctx, *, query=None):
        async with aiohttp.ClientSession() as session:
            student_info = await cc.find_student_info(ctx, session, query)

            timetable_html = await cc.fetch_timetable(session, student_info['id'])

            current_class = cc.find_current_class(timetable_html)

        if current_class:
            period = current_class['period'].text[1:]
            title = current_class['info']['title'] 
            info = cc.format_description(current_class['info']['description'])

            embed = discord.Embed(title=f"Showing Current Class for \"{student_info['title']}\":",
                                  timestamp=datetime.datetime.now(tz=pytz.timezone('Australia/NSW')),    
                                  colour=discord.Colour.from_rgb(80, 250, 123))
            embed.add_field(name=f"Period {period}", value=f'**{title}**\n{info}', inline=False)
            await ctx.send(embed=embed)

        else:
            embed = discord.Embed(title=f"No timetabled class currently for \"{student_info['title']}\":",
                  timestamp=datetime.datetime.now(tz=pytz.timezone('Australia/NSW')),    
                  colour=discord.Colour.from_rgb(80, 250, 123))
            await ctx.send(embed=embed)
            

    @commands.cooldown(1, 10, commands.BucketType.member)
    @commands.command()
    async def today(self, ctx, *, query = None):
        async with aiohttp.ClientSession() as session:
            student_info = await cc.find_student_info(ctx, session, query)   

            timetable_html = await cc.fetch_timetable(session, student_info['id'])

            week, day = cc.find_date(timetable_html)

        await ctx.invoke(self.bot.get_command('timetable'), week, day.name, query=query)

    @commands.cooldown(1, 10, commands.BucketType.member)
    @commands.command()
    async def tomorrow(self, ctx, *, query = None):
        async with aiohttp.ClientSession() as session:
            student_info = await cc.find_student_info(ctx, session, query)   

            timetable_html = await cc.fetch_timetable(session, student_info['id'])

            week, day = cc.find_date(timetable_html)

            if (day.value + 1) > 4:
                day = cc.SchoolDays(0)
                if week == 'a':
                    week = 'b'
                elif week =='b':
                    week = 'a'
            else:
                day = cc.SchoolDays(day.value + 1)

        await ctx.invoke(self.bot.get_command('timetable'), week, day.name, query=query)

    @commands.cooldown(1, 10, commands.BucketType.member)
    @commands.command()
    async def yesterday(self, ctx, *, query = None):
        async with aiohttp.ClientSession() as session:
            student_info = await cc.find_student_info(ctx, session, query)   

            timetable_html = await cc.fetch_timetable(session, student_info['id'])

            week, day = cc.find_date(timetable_html)

            if (day.value - 1) < 0:
                day = cc.SchoolDays(4)
                if week == 'a':
                    week = 'b'
                elif week =='b':
                    week = 'a'
            else:
                day = cc.SchoolDays(day.value - 1)

        await ctx.invoke(self.bot.get_command('timetable'), week, day.name, query=query)

    @commands.cooldown(1, 10, commands.BucketType.member)
    @commands.command()
    async def timetable(self, ctx, week, day_of_week, *, query = None):
        day_index = cc.SchoolDays[day_of_week.upper()].value

        async with aiohttp.ClientSession() as session:
            student_info = await cc.find_student_info(ctx, session, query)   

            timetable_html = await cc.fetch_timetable(session, student_info['id'])

            day_classes = cc.find_day_classes(week.lower(), day_index, timetable_html)

        if day_classes:
            embed = discord.Embed(title=f"Showing Classes for \"{student_info['title']}\" on {day_of_week.upper()}, Week {week.upper()}:",
                                  timestamp=datetime.datetime.now(tz=pytz.timezone('Australia/NSW')),    
                                  colour=discord.Colour.from_rgb(80, 250, 123))
            for day_class in day_classes:
                period = day_class['period'][2:]
                title = day_class['info']['title'] 
                info = cc.format_description(day_class['info']['description'])

                embed.add_field(name=f"Period {period}", value=f'**{title}**\n{info}', inline=False)
        else: 
            embed = discord.Embed(title=f"No periods on {day_of_week.upper()}, Week {week.upper()} for \"{student_info['title']}\".",
                                  timestamp=datetime.datetime.now(tz=pytz.timezone('Australia/NSW')),    
                                  colour=discord.Colour.from_rgb(80, 250, 123))
    
        await ctx.send(embed=embed)

    @commands.cooldown(1, 10, commands.BucketType.member)
    @commands.command()
    async def date(self, ctx, *, query = None):
        async with aiohttp.ClientSession() as session:
            student_info = await cc.find_student_info(ctx, session, query)   

            timetable_html = await cc.fetch_timetable(session, student_info['id'])

            week, day = cc.find_date(timetable_html)

        embed = discord.Embed(title=f"Today's date is {day.name.upper()}, Week {week.upper()}",
                              timestamp=datetime.datetime.now(tz=pytz.timezone('Australia/NSW')),    
                              colour=discord.Colour.from_rgb(80, 250, 123))
        await ctx.send(embed=embed)

def setup(bot):
    bot.add_cog(Timetable(bot))
    