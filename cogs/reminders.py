import traceback
import datetime

import aiohttp
import pytz
import discord
from discord.ext import tasks, commands

import custom_classes as cc

class Reminders(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.current_class = None
        self.class_checker.start()

    def cog_unload(self):
        self.class_checker.cancel()
    
    @commands.command()
    async def force(self, ctx, *, forced_class):
        self.current_class = forced_class
        await ctx.send('success.')

    @tasks.loop(minutes=1)
    async def class_checker(self):
        async with aiohttp.ClientSession() as session:
            student_info = await cc.query_student_info(session, 'chi yung tsai')
            timetable_html = await cc.fetch_timetable(session, student_info['id'])
            current_class = await cc.parse_current_class(timetable_html)

        if self.current_class != current_class:
            self.current_class = current_class

            if current_class = None:
                embed = discord.Embed(title='END OF PERIOD',
                                      description='No class as of now.\n@everyone',
                                      timestamp=datetime.datetime.now(tz=pytz.timezone('Australia/NSW')),    
                                      colour=discord.Colour.from_rgb(241, 250, 250))              
            else:
                embed = discord.Embed(title='NEXT PERIOD',
                                      description='@everyone',
                                      timestamp=datetime.datetime.now(tz=pytz.timezone('Australia/NSW')),    
                                      colour=discord.Colour.from_rgb(241, 250, 250))
            for guild in self.bot.guilds:
                try:
                    await discord.utils.get(guild.text_channels, name='class-updates').send(embed=embed)
                except AttributeError:
                    pass
            print(f'CHANGED: {current_class}')

    @class_checker.before_loop
    async def before_class_checker(self):
        print('waiting..')
        await self.bot.wait_until_ready()

    @class_checker.after_loop
    async def after_class_checker(self):
        if self.class_checker.failed():
            traceback.print_exc()

def setup(bot):
    bot.add_cog(Reminders(bot))
    