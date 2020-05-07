import traceback
import datetime

import pytz
import discord
from discord.ext import commands

class Tasks(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    async def cog_command_error(self, ctx, error):
        if isinstance(error, commands.CheckFailure):
            embed = discord.Embed(title='You are not a contributor.',
                                  description=f'Usage: `>{ctx.command.name} {ctx.command.signature}`',
                                  timestamp=datetime.datetime.now(tz=pytz.timezone('Australia/NSW')),    
                                  colour=discord.Colour.from_rgb(255, 85, 85))
            await ctx.send(embed=embed)     
        else:
            traceback.print_exc()

    async def cog_check(self, ctx): 
        return ctx.bot.database.ready

    def is_contributor():
        async def predicate(ctx):
            if await ctx.bot.database.get_contributor(ctx.author.id):
                return True
        return commands.check(predicate)

    @commands.command()
    @commands.is_owner()
    async def contributor(self, ctx, _id:int):
        user = await self.bot.fetch_user(_id)
        await self.bot.database.enter_contributor(user.id)
        embed = discord.Embed(title=f'{str(userid)} is now a contributor.',
                              timestamp=datetime.datetime.now(tz=pytz.timezone('Australia/NSW')),    
                              colour=discord.Colour.from_rgb(80, 250, 123))
        await ctx.send(embed=embed)


    @commands.group(invoke_without_command=True, help="Displays the public billboard.")
    async def billboard(self, ctx):
        table = await self.bot.database.get_public_tasks()
        embed = discord.Embed(title='Public Billboard',
                              description='Limit of 5 entries on the billboard. *pls dont break*',
                              timestamp=datetime.datetime.now(tz=pytz.timezone('Australia/NSW')),    
                              colour=discord.Colour.from_rgb(80, 250, 123))
        for row in table:
            author = await self.bot.fetch_user(row["author"])
            embed.add_field(name=f'ID: {row["id"]}',
                            value='\n'.join([f'`[AUTHOR]`: {str(author)}',
                                             f'`[DESCRIPTION]`: {row["description"]}']),
                            inline=False)
        await ctx.send(embed=embed)

    @billboard.command(help="Create an entry on the public billboard.")
    @is_contributor()
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

    @billboard.command(help="Remove an entry from the public billboard")
    @is_contributor()
    async def delete(self, ctx, _id:int):
        deleted_row = await self.bot.database.delete_public_task(_id)
        author = await self.bot.fetch_user(deleted_row["author"])
        embed = discord.Embed(title='Deleted Entry from Billboard',
                              description='\n'.join([f'`[AUTHOR]`: {str(author)}',
                                                     f'`[DESCRIPTION]`: {deleted_row["description"]}']),
                              timestamp=datetime.datetime.now(tz=pytz.timezone('Australia/NSW')),    
                              colour=discord.Colour.from_rgb(80, 250, 123))
        await ctx.send(embed=embed)

def setup(bot):
    bot.add_cog(Tasks(bot))
