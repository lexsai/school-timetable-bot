import traceback
import datetime

import pytz
import aiohttp
import discord
from discord.ext import tasks, commands

class Reminders(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.current_class = None
        self.class_checker.start()

    def cog_unload(self):
        self.class_checker.cancel()

    @commands.command()
    async def force_class(self, ctx, *, param):
        self.current_class = param

        await ctx.send('success.')

    @tasks.loop(minutes=1)
    async def class_checker(self):
        timetable_cog = self.bot.get_cog('Timetable')

        async with aiohttp.ClientSession() as session:
            student_info = await timetable_cog.query_student_info(session, 'chi yung tsai')
            timetable_html = await timetable_cog.fetch_timetable(session, student_info['id'])
            current_class = await timetable_cog.parse_current_class(timetable_html)

        if self.current_class != current_class:
            self.current_class = current_class
            for guild in self.bot.guilds:
                embed = discord.Embed(title='NEXT PERIOD',
                                      description=f'@everyone',
                                      timestamp=datetime.datetime.now(tz=pytz.timezone('Australia/NSW')),    
                                      colour=discord.Colour.from_rgb(241, 250, 250))
                await guild.text_channels[0].send(embed=embed)
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
    