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
        self.bot.current_class = None
        self.class_checker.start()

    def cog_unload(self):
        self.class_checker.cancel()

    @tasks.loop(minutes=1)
    async def class_checker(self):
        async with aiohttp.ClientSession() as session:
            student_info = await cc.query_student_info(session, 'chi yung tsai')
            timetable_html = await cc.fetch_timetable(session, student_info['id'])
            current_class = cc.find_current_class(timetable_html)

        if self.bot.current_class != current_class:
            self.bot.current_class = current_class

            if current_class is None:
                embed = discord.Embed(title='END OF PERIOD',
                                      description='No class as of now.',
                                      timestamp=datetime.datetime.now(tz=pytz.timezone('Australia/NSW')),    
                                      colour=discord.Colour.from_rgb(241, 250, 250))              
            else:
                embed = discord.Embed(title='NEXT PERIOD',
                                      timestamp=datetime.datetime.now(tz=pytz.timezone('Australia/NSW')),    
                                      colour=discord.Colour.from_rgb(241, 250, 250))
            for guild in self.bot.guilds:
                try:
                    await discord.utils.get(guild.text_channels, name='class-updates').send('@everyone', embed=embed)
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
    