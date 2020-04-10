import datetime
import json
import traceback

import aiohttp
import pytz
import discord
from discord.ext import commands
from bs4 import BeautifulSoup

class Timetable(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    async def fetch_student(self, session, query):
        params = {
            'query' : query,
            'search_inactive' : 'false',
            'show_external_id' : 'false'
        }

        resp = await session.request('get', 'https://web1.normanhurb-h.schools.nsw.edu.au/timetables/ajax/searchStudents', params = params)
        print('[QUERY]', resp.status, resp.reason)  
        return await resp.text()

    async def fetch_timetable(self, session, student_id):
        resp = await session.request('get', 
                                     'https://web1.normanhurb-h.schools.nsw.edu.au/timetables/timetable', 
                                      params = {'student' : str(student_id)})

        print('[TIMETABLE]', resp.status, resp.reason)  
        return await resp.text()

    async def parse_today_classes(self, html):
        soup = BeautifulSoup(html, 'html.parser')

        today_classes_html = soup.findAll('td', {'class' : 'timetable-dayperiod today'})
        today_classes = [{'title' : today_class.find('strong').text,
                          'info' : today_class.find('br').text} for today_class in today_classes_html]

        return today_classes

    async def parse_current_class(self, html):
        soup = BeautifulSoup(html, 'html.parser')

        current_classes_html = soup.findAll('tr', {'class' : 'now'})

        try:
            current_class_html = [current.find('td', {'class' : 'timetable-dayperiod today'}) 
                                  for current in current_classes_html 
                                  if current.find('td', {'class' : 'timetable-dayperiod today'}) != None][0]
        except IndexError:
            return None

        current_class = {'title' : current_class_html.find('strong').text, 
                         'info' :  current_class_html.find('br').text}    

        return current_class

    async def query_student_info(self, session, query):
        try: 
            query_resp = await self.fetch_student(session, query)
            student_info = json.loads(query_resp)['results'][0]
        except (IndexError, TypeError) as e:
            raise commands.BadArgument
            return

        return student_info

    async def find_student_info(self, ctx, session, query):
        if query is not None:
            student_info = await self.query_student_info(session, query)
        else:
            try:
                cached_data = [role.name.split('|') for role in ctx.author.roles if len(role.name.split('|')) == 2][0]
            except:
                raise commands.BadArgument

            student_info = {
                'title' : cached_data[0],
                'id' : cached_data[1]
            }

        return student_info

    @commands.command()
    async def identify(self, ctx, *, query):
        async with aiohttp.ClientSession() as session:
            student_info = await self.query_student_info(session, query)

        title_with_year = student_info['title']
        title = student_info['title'].split(' - ')[0]
        student_id = str(student_info['id'])
        
        if f'{title}|{student_id}' in [role.name for role in ctx.author.roles]:
            embed = discord.Embed(title='Cannot assign role.',
                                  description=f'{ctx.author.mention} already identified as "{title_with_year}"',
                                  timestamp=datetime.datetime.now(tz=pytz.timezone('Australia/NSW')),    
                                  colour=discord.Colour.from_rgb(255, 85, 85))
            await ctx.send(embed=embed)
        else:
            role = await ctx.guild.create_role(name=f'{title}|{student_id}')
            await ctx.author.add_roles(role)

            embed = discord.Embed(title='Assigned role.',
                      description=f'{ctx.author.mention} identified as "{title_with_year}"',
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
            student_info = await self.find_student_info(ctx, session, query)

            timetable_html = await self.fetch_timetable(session, student_info['id'])

            current_class = await self.parse_current_class(timetable_html)

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
            student_info = await self.find_student_info(ctx, session, query)   

            timetable_html = await self.fetch_timetable(session, student_info['id'])

            today_classes = await self.parse_today_classes(timetable_html)


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
    