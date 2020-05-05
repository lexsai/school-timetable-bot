import datetime

import pytz
import discord
from discord.ext import commands

class Tasks(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    async def cog_check(self, ctx): 
        return ctx.bot.database.ready and 'CONTRIBUTOR' in [role.name for role in ctx.author.roles]

    @commands.group(invoke_without_command=True)
    async def billboard(self, ctx):
        table = await self.bot.database.get_public_tasks()
        embed = discord.Embed(title='Public Billboard',
                              description='Limit of 5 entries on the billboard. *pls dont break*',
                              timestamp=datetime.datetime.now(tz=pytz.timezone('Australia/NSW')),    
                              colour=discord.Colour.from_rgb(80, 250, 123))
        for row in table:
            embed.add_field(name=f'ID: {row["id"]}',
                            value='\n'.join([f'`[AUTHOR]`: {str(await self.bot.fetch_user(row["author"]))}',
                                             f'`[DESCRIPTION]`: {row["description"]}']),
                            inline=False)
        await ctx.send(embed=embed)

    @billboard.command()
    async def create(self, ctx, *, description):
        entry_limit = await self.bot.database.get_public_task_amount()
        if entry_limit < 5:
            await self.bot.database.enter_public_task(ctx.author.id, description)
            embed = discord.Embed(title='Created Entry on Billboard',
                                  description='\n'.join([f'`[AUTHOR]`: {ctx.author.mention}',
                                                         f'`[DESCRIPTION]`: {description}']),
                                  timestamp=datetime.datetime.now(tz=pytz.timezone('Australia/NSW')),    
                                  colour=discord.Colour.from_rgb(80, 250, 123))
            await ctx.send(embed=embed)

    @billboard.command()
    async def delete(self, ctx, identity:int):
        deleted_row = await self.bot.database.delete_public_task(identity)
        embed = discord.Embed(title='Deleted Entry from Billboard',
                              description='\n'.join([f'`[AUTHOR]`: {str(await self.bot.fetch_user(deleted_row["author"]))}',
                                                     f'`[DESCRIPTION]`: {deleted_row["description"]}']),
                              timestamp=datetime.datetime.now(tz=pytz.timezone('Australia/NSW')),    
                              colour=discord.Colour.from_rgb(80, 250, 123))
        await ctx.send(embed=embed)

def setup(bot):
    bot.add_cog(Tasks(bot))
